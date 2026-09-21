import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

const emptyData = {
  hasNewDocs: false,
  pendingCount: 0,
  soCanhBao: 0,
  soSuKien: 0,
  warnings: [],
  nghiaVu: [],
  conSoChot: [],
  hanChot: [],
  chuaHieuLuc: [],
  vbTuChet: [],
  vbSapChet: [],
  events: [],
  suKienHieuLuc: [],
  impact: [],
  coQuanVbBo: [],
  namVbBo: [],
  insights: {
    luotVien: 0,
    thayThe: 0,
    baiBo: 0,
    vbNhieuCanCu: 0,
    luotLuatMoi: 0,
    topCanCu: [],
    theoNam: [],
    tapTrung: { theoLoai: [], theoChuDe: [] },
    tinCay: { tb: 0, tong: 0, ocr: 0, duoi80: 0 },
    uuTien: []
  }
};

interface DataContextType {
  data: any;
  loading: boolean;
  error: string | null;
  refreshData: () => void;
}

const DataContext = createContext<DataContextType>({
  data: emptyData,
  loading: false,
  error: null,
  refreshData: () => {},
});

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [data, setData] = useState<any>(emptyData);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      fetch('http://localhost:8000/api/v1/legal-data').then(res => res.ok ? res.json() : {} as any),
      fetch('http://localhost:8000/api/v1/auditing/warnings').then(res => res.ok ? res.json() : {} as any),
      fetch('http://localhost:8000/api/v1/analytics').then(res => res.ok ? res.json() : {} as any),
      fetch('http://localhost:8000/api/v1/review/pending').then(res => res.ok ? res.json() : {} as any),
      fetch('http://localhost:8000/api/v1/system/status').then(res => res.ok ? res.json() : {} as any)
    ])
      .then(([legalData, warningsData, analyticsData, reviewData, systemData]) => {
        
        const nghiaVuList = reviewData?.nghiaVu || [];
        const conSoChotList = reviewData?.conSoChot || [];
        const combinedReviewCount = nghiaVuList.length + conSoChotList.length;

        setData({
          ...emptyData,
          hasNewDocs: systemData?.has_new_docs || false,
          pendingCount: combinedReviewCount,
          nghiaVu: legalData.nghiaVu || [],
          conSoChot: legalData.conSoChot || [],
          hanChot: legalData.hanChot || [],
          chuaHieuLuc: legalData.chuaHieuLuc || [],
          vbTuChet: legalData.vbTuChet || [],
          vbSapChet: legalData.vbSapChet || [],
          events: legalData.events || [],
          suKienHieuLuc: legalData.suKienHieuLuc || [],
          impact: legalData.impact || [],
          soCanhBao: (warningsData.warnings || []).length,
          soSuKien: (legalData.events || []).length,
          warnings: warningsData.warnings || [],
          insights: {
            ...emptyData.insights,
            ...(analyticsData.insights || {}),
            uuTien: warningsData.warnings || []
          }
        });
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch legal data:', err);
        setError('Cannot connect to backend.');
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <DataContext.Provider value={{ data, loading, error, refreshData: fetchData }}>
      {children}
    </DataContext.Provider>
  );
};

export const useData = () => useContext(DataContext);
