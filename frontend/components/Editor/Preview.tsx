'use client';

import { useEffect, useRef } from 'react';

interface PreviewProps {
  files: Record<string, string>;
  stack: string;
}

export default function Preview({ files, stack }: PreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (!iframeRef.current) return;

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
  }, [files, stack]);

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="bg-[#111111] px-6 py-3 border-b border-gray-800 flex items-center justify-between">
        <span className="text-gray-300 text-sm flex items-center gap-2">
          <span>👁️</span>
          <span>Live Preview</span>
        </span>
        <span className="text-xs text-gray-500 uppercase bg-blue-500/10 px-2 py-1 rounded border border-blue-500/20 text-blue-400">
          {stack}
        </span>
      </div>
      <div className="flex-1 overflow-hidden bg-white">
        <iframe
          ref={iframeRef}
          className="w-full h-full border-none"
          title="Portfolio Preview"
        />
      </div>
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
