import React, { useState, useEffect } from 'react';

interface Template {
  id: string;
  name: string;
  style: string;
  layout: string;
  description: string;
  animation_level: number;
  features: string[];
  supported_stacks: string[];
  color_schemes: [string, string][];
}

interface TemplateGridProps {
  sessionId: string;
  stack: string;
  onTemplateSelect: (templateId: string) => void;
}

interface PaginationData {
  templates: Template[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export const TemplateGrid: React.FC<TemplateGridProps> = ({ sessionId, stack, onTemplateSelect }) => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTemplates, setTotalTemplates] = useState(0);
  const TEMPLATES_PER_PAGE = 20;

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        const filterParam = filter === 'all' ? '' : `&style=${filter}`;
        const response = await fetch(`/api/templates?stack=${stack}&page=${currentPage}&limit=${TEMPLATES_PER_PAGE}${filterParam}`);
        const data: PaginationData = await response.json();
        setTemplates(data.templates);
        setTotalPages(data.pages);
        setTotalTemplates(data.total);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch templates:', error);
        setLoading(false);
      }
    };

    fetchTemplates();
  }, [stack, filter, currentPage]);

  const styles = templates.map(t => t.style);
  const uniqueStyles = Array.from(new Set(styles));

  const handleSelect = (templateId: string) => {
    setSelectedTemplate(templateId);
    onTemplateSelect(templateId);
  };

  const handlePreviousPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };

  const handleFilterChange = (newFilter: string) => {
    setFilter(newFilter);
    setCurrentPage(1);
  };

  if (loading) {
    return <div className="template-loading">Loading templates...</div>;
  }

  return (
    <div className="template-selector">
      <div className="template-header">
        <h2>Choose Your Portfolio Template</h2>
        <p>Select from {totalTemplates} professional designs</p>
      </div>

      <div className="template-filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => handleFilterChange('all')}
        >
          All Templates
        </button>
        {uniqueStyles.map(style => (
          <button
            key={style}
            className={`filter-btn ${filter === style ? 'active' : ''}`}
            onClick={() => handleFilterChange(style)}
          >
            {style.charAt(0).toUpperCase() + style.slice(1)}
          </button>
        ))}
      </div>

      <div className="template-grid">
        {templates.map(template => (
          <div
            key={template.id}
            className={`template-card ${selectedTemplate === template.id ? 'selected' : ''}`}
            onClick={() => handleSelect(template.id)}
          >
            <div className="template-preview">
              <div className="color-preview">
                {template.color_schemes.slice(0, 3).map((scheme, idx) => (
                  <div key={idx} className="color-swatch-row">
                    <div className="color-swatch" style={{ backgroundColor: scheme[0] }}></div>
                    <div className="color-swatch" style={{ backgroundColor: scheme[1] }}></div>
                  </div>
                ))}
              </div>
            </div>

            <div className="template-info">
              <h3>{template.name}</h3>
              <p className="description">{template.description}</p>

              <div className="template-meta">
                <span className="style-badge">{template.style}</span>
                <span className="layout-badge">{template.layout.replace('_', ' ')}</span>
                <span className="animation-badge">
                  {'🎬'.repeat(template.animation_level)}
                </span>
              </div>

              <div className="template-features">
                {template.features.slice(0, 3).map(feature => (
                  <span key={feature} className="feature-tag">
                    {feature}
                  </span>
                ))}
              </div>

              {selectedTemplate === template.id && (
                <div className="selected-indicator">✓ Selected</div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Controls */}
      {totalTemplates > 0 && (
        <div className="pagination-container">
          <button
            className="pagination-btn prev-btn"
            onClick={handlePreviousPage}
            disabled={currentPage === 1}
          >
            ← Previous
          </button>

          <div className="pagination-info">
            <span className="page-indicator">
              Page <strong>{currentPage}</strong> of <strong>{totalPages}</strong>
            </span>
            <span className="template-count">
              ({totalTemplates} total templates)
            </span>
          </div>

          <button
            className="pagination-btn next-btn"
            onClick={handleNextPage}
            disabled={currentPage === totalPages}
          >
            Next →
          </button>
        </div>
      )}

      <style jsx>{`
        .template-selector {
          padding: 2rem;
        }

        .template-header {
          text-align: center;
          margin-bottom: 3rem;
        }

        .template-header h2 {
          font-size: 2rem;
          margin-bottom: 0.5rem;
        }

        .template-header p {
          color: #666;
        }

        .template-filters {
          display: flex;
          gap: 1rem;
          margin-bottom: 2rem;
          flex-wrap: wrap;
          justify-content: center;
        }

        .filter-btn {
          padding: 0.5rem 1.5rem;
          border: 2px solid #ddd;
          background: white;
          border-radius: 25px;
          cursor: pointer;
          transition: all 0.3s;
          font-weight: 500;
        }

        .filter-btn:hover {
          border-color: #667eea;
        }

        .filter-btn.active {
          background: #667eea;
          color: white;
          border-color: #667eea;
        }

        .template-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
          gap: 2rem;
        }

        .template-card {
          border: 2px solid #eee;
          border-radius: 12px;
          overflow: hidden;
          cursor: pointer;
          transition: all 0.3s;
          background: white;
        }

        .template-card:hover {
          border-color: #667eea;
          box-shadow: 0 10px 30px rgba(102, 126, 234, 0.1);
          transform: translateY(-5px);
        }

        .template-card.selected {
          border-color: #667eea;
          background: #f7faff;
        }

        .template-preview {
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
          height: 150px;
          padding: 1rem;
        }

        .color-preview {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          height: 100%;
          justify-content: center;
        }

        .color-swatch-row {
          display: flex;
          gap: 0.5rem;
        }

        .color-swatch {
          flex: 1;
          height: 30px;
          border-radius: 4px;
          border: 1px solid rgba(0, 0, 0, 0.1);
        }

        .template-info {
          padding: 1.5rem;
        }

        .template-info h3 {
          font-size: 1.2rem;
          margin-bottom: 0.5rem;
        }

        .description {
          color: #666;
          font-size: 0.9rem;
          margin-bottom: 1rem;
        }

        .template-meta {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
          flex-wrap: wrap;
        }

        .style-badge,
        .layout-badge,
        .animation-badge {
          display: inline-block;
          padding: 0.3rem 0.8rem;
          background: #f0f0f0;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .animation-badge {
          background: #ffe8f0;
        }

        .template-features {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
          flex-wrap: wrap;
        }

        .feature-tag {
          display: inline-block;
          padding: 0.25rem 0.6rem;
          background: #f5f5f5;
          border-radius: 3px;
          font-size: 0.75rem;
          color: #555;
        }

        .selected-indicator {
          text-align: center;
          color: #667eea;
          font-weight: 600;
          padding-top: 0.5rem;
          border-top: 2px solid #667eea;
        }

        .template-loading {
          text-align: center;
          padding: 2rem;
          color: #666;
        }

        .pagination-container {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 2rem;
          margin-top: 3rem;
          padding: 2rem;
          background: #f9f9f9;
          border-radius: 12px;
        }

        .pagination-btn {
          padding: 0.75rem 1.5rem;
          border: 2px solid #667eea;
          background: white;
          color: #667eea;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s;
          font-size: 0.95rem;
        }

        .pagination-btn:hover:not(:disabled) {
          background: #667eea;
          color: white;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .pagination-btn:disabled {
          border-color: #ccc;
          color: #ccc;
          cursor: not-allowed;
          background: #f5f5f5;
        }

        .pagination-info {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 0.5rem;
          min-width: 200px;
        }

        .page-indicator {
          font-size: 1.1rem;
          color: #333;
          font-weight: 500;
        }

        .page-indicator strong {
          color: #667eea;
        }

        .template-count {
          font-size: 0.9rem;
          color: #888;
        }

        @media (max-width: 768px) {
          .template-grid {
            grid-template-columns: 1fr;
          }

          .pagination-container {
            flex-direction: column;
            gap: 1rem;
          }

          .pagination-btn {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
};

export default TemplateGrid;
