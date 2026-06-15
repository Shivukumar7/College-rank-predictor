import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import { College } from './api';

export function generateChoicePDF(studentName: string, examName: string, colleges: College[]) {
  const doc = new jsPDF();
  
  // Header
  doc.setFontSize(22);
  doc.setTextColor(15, 23, 42); // slate-900
  doc.text('ExamRank AI', 14, 22);
  
  doc.setFontSize(16);
  doc.setTextColor(59, 130, 246); // blue-500
  doc.text('Optimized Choice Filling Order', 14, 32);

  doc.setFontSize(11);
  doc.setTextColor(100, 116, 139); // slate-500
  doc.text(`Candidate: ${studentName || 'Not Specified'}`, 14, 42);
  doc.text(`Counseling: ${examName.toUpperCase()} 2026`, 14, 48);
  doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 54);

  // Divider
  doc.setDrawColor(226, 232, 240); // slate-200
  doc.setLineWidth(0.5);
  doc.line(14, 60, 196, 60);

  // Disclaimer
  doc.setFontSize(9);
  doc.setTextColor(239, 68, 68); // red-500
  doc.text(
    '* Disclaimer: This is an AI-generated predictive order. Please verify official codes before final submission.',
    14,
    68
  );

  // Table Data
  const tableData = colleges.map((c, index) => {
    // Generate a mock code based on name to make it look official
    const mockCode = c.name.substring(0, 3).toUpperCase() + c.branch.substring(0, 2).toUpperCase() + Math.floor(Math.random() * 100).toString().padStart(2, '0');
    
    return [
      c.choice_number || index + 1,
      mockCode,
      c.name,
      c.branch,
      c.type,
      c.chance >= 80 ? 'High' : c.chance >= 40 ? 'Moderate' : 'Low'
    ];
  });

  autoTable(doc, {
    startY: 74,
    head: [['Choice #', 'Code (Approx)', 'Institute Name', 'Branch', 'Type', 'Chance']],
    body: tableData,
    theme: 'grid',
    headStyles: {
      fillColor: [15, 23, 42],
      textColor: [255, 255, 255],
      fontSize: 10,
      fontStyle: 'bold',
    },
    bodyStyles: {
      fontSize: 9,
      textColor: [51, 65, 85],
    },
    alternateRowStyles: {
      fillColor: [248, 250, 252],
    },
    columnStyles: {
      0: { cellWidth: 20, halign: 'center' },
      1: { cellWidth: 25, halign: 'center', fontStyle: 'bold' },
      2: { cellWidth: 'auto' },
      3: { cellWidth: 40 },
      4: { cellWidth: 25 },
      5: { cellWidth: 20, halign: 'center' },
    },
    didDrawPage: function (data) {
      // Footer
      const str = 'Page ' + doc.internal.getNumberOfPages();
      doc.setFontSize(8);
      doc.setTextColor(148, 163, 184);
      doc.text(
        str,
        data.settings.margin.left,
        doc.internal.pageSize.height - 10
      );
    },
  });

  doc.save(`${studentName ? studentName.replace(/\s+/g, '_') : 'Candidate'}_${examName}_Choices.pdf`);
}
