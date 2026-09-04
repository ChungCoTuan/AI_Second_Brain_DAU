import React from 'react';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

interface FaithfulnessScoreProps {
  score: number;
}

const FaithfulnessScore: React.FC<FaithfulnessScoreProps> = ({ score }) => {
  let status = 'faith-high';
  let Icon = ShieldCheck;
  
  if (score < 60) {
    status = 'faith-low';
    Icon = ShieldX;
  } else if (score < 85) {
    status = 'faith-medium';
    Icon = ShieldAlert;
  }

  return (
    <div className={`faith-score ${status}`}>
      <Icon size={16} />
      <span>{score}% Trust</span>
    </div>
  );
};

export default FaithfulnessScore;
