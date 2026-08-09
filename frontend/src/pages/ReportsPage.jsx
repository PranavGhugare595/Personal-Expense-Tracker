import { useState, useRef } from 'react';
import { FileText, Download, FileSpreadsheet } from 'lucide-react';
import api from '../utils/api';
import AnalyticsPage from './AnalyticsPage';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import './ReportsPage.css';

export default function ReportsPage() {
  const [downloading, setDownloading] = useState(false);
  const reportRef = useRef(null);

  const downloadCSV = async () => {
    try {
      // The easiest way is to construct the URL and trigger a download via window.open
      // or fetch it as a blob and download it.
      const res = await api.get('/api/v1/reports/csv', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `expense_report_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      console.error('Failed to download CSV:', err);
      alert('Failed to download CSV report');
    }
  };

  const downloadPDF = async () => {
    if (!reportRef.current) return;
    setDownloading(true);
    
    try {
      const canvas = await html2canvas(reportRef.current, {
        scale: 2,
        useCORS: true,
        logging: false
      });
      
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save(`financial_report_${new Date().toISOString().split('T')[0]}.pdf`);
    } catch (err) {
      console.error('Failed to generate PDF:', err);
      alert('Failed to generate PDF report');
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="reports-page">
      <div className="page-header">
        <h1>Reports & Exports</h1>
        <div className="export-actions">
          <button className="btn-export csv" onClick={downloadCSV}>
            <FileSpreadsheet size={18} />
            Download CSV
          </button>
          <button className="btn-export pdf" onClick={downloadPDF} disabled={downloading}>
            <Download size={18} />
            {downloading ? 'Generating PDF...' : 'Download PDF'}
          </button>
        </div>
      </div>
      
      <div className="report-preview-banner">
        <FileText size={20} />
        <span>The analytics view below will be included in your PDF report. Adjust the filters in the Analytics section before downloading.</span>
      </div>

      <div className="report-preview-container" ref={reportRef}>
        <AnalyticsPage />
      </div>
    </div>
  );
}
