import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

const emptyData = {
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
      fetch('http://localhost:8000/api/v1/analytics').then(res => res.ok ? res.json() : {} as any)
    ])
      .then(([apiData, auditingData, analyticsData]) => {
        setData({
          ...emptyData,
          nghiaVu: apiData.nghiaVu || [],
          conSoChot: apiData.conSoChot || [],
          hanChot: apiData.hanChot || [],
          chuaHieuLuc: apiData.chuaHieuLuc || [],
          vbTuChet: apiData.vbTuChet || [],
          vbSapChet: apiData.vbSapChet || [],
          events: apiData.events || [],
          suKienHieuLuc: apiData.suKienHieuLuc || [],
          impact: apiData.impact || [],
          insights: {
            ...emptyData.insights,
            ...(analyticsData.insights || {}),
            uuTien: auditingData.warnings || []
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
