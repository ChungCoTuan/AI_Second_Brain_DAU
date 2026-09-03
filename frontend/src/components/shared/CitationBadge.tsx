import React from 'react';
import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';

interface CitationBadgeProps {
  documentId: string;
  sourceText: string;
  pageNumber?: number;
}

const CitationBadge: React.FC<CitationBadgeProps> = ({ documentId, sourceText, pageNumber }) => {
  const handlePdfClick = (e: React.MouseEvent) => {
    if (pageNumber) {
      // Giả lập nhảy trang trong file PDF
      e.preventDefault();
      alert(`Mở file gốc và nhảy tới trang ${pageNumber}`);
    }
  };

  return (
    <Link to={`/compare/${documentId}`} className="citation-badge" onClick={handlePdfClick}>
      <FileText size={14} />
      <span>{sourceText}</span>
    </Link>
  );
};

export default CitationBadge;
