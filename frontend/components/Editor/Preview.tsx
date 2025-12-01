'use client';

import { useEffect, useRef, useState } from 'react';

interface PreviewProps {
  files: Record<string, string>;
  stack: string;
}

export default function Preview({ files, stack }: PreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!iframeRef.current) return;

    setIsLoading(true);

    let previewHTML = '';

    if (stack === 'react') {
      previewHTML = generateReactPreview(files);
    } else if (stack === 'nextjs') {
      previewHTML = generateNextJsPreview(files);
    } else if (stack === 'vue') {
      previewHTML = generateVuePreview(files);
    } else if (stack === 'svelte') {
      previewHTML = generateSveltePreview(files);
    }

    iframeRef.current.srcdoc = previewHTML;

    const timer = setTimeout(() => setIsLoading(false), 1500);
    return () => clearTimeout(timer);
  }, [files, stack]);

  return (
    <div className="h-full flex flex-col bg-white relative">
      {/* Loading Animation */}
      {isLoading && (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center z-10">
          <div className="text-center">
            {/* Animated Portfolio Icon */}
            <div className="relative w-24 h-24 mx-auto mb-6">
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-500 to-cyan-500 rounded-2xl animate-pulse"></div>
              <div className="absolute inset-2 bg-gray-900 rounded-xl flex items-center justify-center">
                <svg className="w-12 h-12 text-blue-400 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>

            {/* Loading Text */}
            <h3 className="text-xl font-semibold text-white mb-2">Preparing Your Portfolio</h3>
            <p className="text-gray-400 text-sm mb-6">Crafting something amazing...</p>

            {/* Progress Bar */}
            <div className="w-64 h-1 bg-gray-700 rounded-full overflow-hidden mx-auto">
              <div className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full animate-[loading_1.5s_ease-in-out_infinite]"></div>
            </div>

            {/* Spinning Dots */}
            <div className="flex gap-2 justify-center mt-6">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            </div>
          </div>
        </div>
      )}

      {/* Preview Content */}
      <div className="flex-1 overflow-hidden bg-white">
        <iframe
          ref={iframeRef}
          className="w-full h-full border-none"
          title="Portfolio Preview"
        />
      </div>

      {/* Keyframe Animation */}
      <style jsx>{`
        @keyframes loading {
          0% { transform: translateX(-100%); }
          50% { transform: translateX(0%); }
          100% { transform: translateX(100%); }
        }
      `}</style>
    </div>
  );
}

function generateReactPreview(files: Record<string, string>): string {
  // Check for CSS in multiple possible locations
  const css = files['src/index.css'] || files['src/styles.css'] || files['src/App.css'] || '';
  let appCode = files['src/App.jsx'] || files['src/App.tsx'] || '';

  // Extract destructured imports before removing them
  const destructuredImports = new Set<string>();
  const importMatch = appCode.match(/import\s+\{([^}]+)\}\s+from\s+['"]react['"]/);
  if (importMatch) {
    const imports = importMatch[1].split(',').map(s => s.trim());
    imports.forEach(imp => destructuredImports.add(imp));
  }

  // Remove all import statements (they can't be used in inline scripts)
  appCode = appCode.replace(/import\s+.*from\s+['"][^'"]*['"];?/g, '');
  appCode = appCode.replace(/import\s+['"][^'"]*['"];?/g, '');

  // Build React hook extraction code
  const hookExtraction = Array.from(destructuredImports).length > 0
    ? `const { ${Array.from(destructuredImports).join(', ')} } = React;`
    : '';

  appCode = appCode.replace(/export\s+default\s+App/g, '// App component defined above');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>${css}</style>
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    try {
      ${hookExtraction}
      ${appCode}
      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(<App />);
    } catch (error) {
      console.error('Preview Error:', error);
      document.getElementById('root').innerHTML = '<div style="padding: 2rem; color: red; font-family: monospace;">Error: ' + error.message + '</div>';
    }
  </script>
</body>
</html>
  `.trim();
}

function generateNextJsPreview(files: Record<string, string>): string {
  // Check for CSS in multiple possible locations
  const css = files['app/globals.css'] || files['src/styles.css'] || files['src/index.css'] || '';
  let appCode = files['app/page.tsx'] || '';

  appCode = appCode.replace(/"use client"\s*/g, '');

  // Extract destructured imports before removing them
  const destructuredImports = new Set<string>();
  const importMatch = appCode.match(/import\s+\{([^}]+)\}\s+from\s+['"]react['"]/);
  if (importMatch) {
    const imports = importMatch[1].split(',').map(s => s.trim());
    imports.forEach(imp => destructuredImports.add(imp));
  }

  // Remove all import statements (they can't be used in inline scripts)
  appCode = appCode.replace(/import\s+.*from\s+['"][^'"]*['"];?/g, '');
  appCode = appCode.replace(/import\s+['"][^'"]*['"];?/g, '');

  // Build React hook extraction code
  const hookExtraction = Array.from(destructuredImports).length > 0
    ? `const { ${Array.from(destructuredImports).join(', ')} } = React;`
    : '';

  appCode = appCode.replace(/export\s+default\s+function\s+\w+\s*\(/g, 'function App(');
  appCode = appCode.replace(/export\s+default\s+function\s+\w+\(/g, 'function App(');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>${css}</style>
  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel">
    try {
      ${hookExtraction}
      ${appCode}
      const root = ReactDOM.createRoot(document.getElementById('root'));
      root.render(<App />);
    } catch (error) {
      console.error('Preview Error:', error);
      document.getElementById('root').innerHTML = '<div style="padding: 2rem; color: red; font-family: monospace;">Error: ' + error.message + '</div>';
    }
  </script>
</body>
</html>
  `.trim();
}

function generateVuePreview(files: Record<string, string>): string {
  // Check for CSS in multiple possible locations
  const css = files['src/style.css'] || files['src/styles.css'] || files['src/index.css'] || '';
  let appVue = files['src/App.vue'] || '';

  const templateMatch = appVue.match(/<template>([\s\S]*?)<\/template>/);
  const scriptMatch = appVue.match(/<script[^>]*>([\s\S]*?)<\/script>/);

  let template = templateMatch ? templateMatch[1].trim() : '<div>No template found</div>';
  let script = scriptMatch ? scriptMatch[1].trim() : '';

  // Remove import statements
  script = script.replace(/import\s+\{[^}]+\}\s+from\s+['"]vue['"];?\s*/g, '');
  script = script.replace(/import\s+.*from\s+['"].*['"];?\s*/g, '');

  // Escape template special characters
  template = template.replace(/`/g, '\\`');
  template = template.replace(/\$\{/g, '\\${');

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>${css}</style>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
</head>
<body>
  <div id="app"></div>
  <script>
    try {
      const { createApp, ref, onMounted, onBeforeUnmount } = Vue;
      const App = {
        template: \`${template}\`,
        setup() {
          ${script}
          return {
            isScrolled,
            scrollToSection
          };
        }
      };
      createApp(App).mount('#app');
    } catch (error) {
      console.error('Preview Error:', error);
      document.getElementById('app').innerHTML = '<div style="padding: 2rem; color: red; font-family: monospace;">Error: ' + error.message + '</div>';
    }
  </script>
</body>
</html>
  `.trim();
}

function generateSveltePreview(files: Record<string, string>): string {
  // Check for CSS in multiple possible locations
  const css = files['src/app.css'] || files['src/styles.css'] || files['src/index.css'] || '';
  let appSvelte = files['src/App.svelte'] || '';

  const scriptMatch = appSvelte.match(/<script>([\s\S]*?)<\/script>/);
  const htmlMatch = appSvelte.replace(/<script>[\s\S]*?<\/script>/, '').replace(/<style>[\s\S]*?<\/style>/, '').trim();

  let script = scriptMatch ? scriptMatch[1].trim() : '';
  let html = htmlMatch;

  html = html.replace(/<svelte:window[^>]*>/g, '');
  html = html.replace(/<\/svelte:window>/g, '');
  html = html.replace(/class:/g, 'data-class-');
  html = html.replace(/on:(\w+)=\{([^}]+)\}/g, (match, event, handler) => {
    return `on${event}="${handler.replace(/\(\)/g, '(event)')}"`
      ;
  });

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>${css}</style>
</head>
<body>
  <div id="app">${html}</div>
  <script>
    try {
      ${script}
      window.addEventListener('scroll', () => {
        handleScroll();
        const nav = document.querySelector('nav');
        if (nav) {
          if (scrolled) {
            nav.classList.add('scrolled');
          } else {
            nav.classList.remove('scrolled');
          }
        }
      });
      window.scrollToSection = scrollToSection;
    } catch (error) {
      console.error('Preview Error:', error);
      document.getElementById('app').innerHTML = '<div style="padding: 2rem; color: red; font-family: monospace;">Error: ' + error.message + '</div>';
    }
  </script>
</body>
</html>
  `.trim();
}
