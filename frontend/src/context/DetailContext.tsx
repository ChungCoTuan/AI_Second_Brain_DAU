import React, { createContext, useContext, useState, ReactNode } from 'react';

interface DetailContextType {
  docId: string | null;
  openDetail: (id: string) => void;
  closeDetail: () => void;
}

const DetailContext = createContext<DetailContextType | undefined>(undefined);

export const DetailProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [docId, setDocId] = useState<string | null>(null);

  const openDetail = (id: string) => {
    setDocId(id);
  };

  const closeDetail = () => {
    setDocId(null);
  };

  return (
    <DetailContext.Provider value={{ docId, openDetail, closeDetail }}>
      {children}
    </DetailContext.Provider>
  );
};

export const useDetail = () => {
  const context = useContext(DetailContext);
  if (context === undefined) {
    throw new Error('useDetail must be used within a DetailProvider');
  }
  return context;
};
