interface HeatmapProps {
  scores: Array<{
    company: { ticker: string; name: string };
    score: number;
    article_count: number;
  }>;
  onStockClick: (ticker: string) => void;
}

export const Heatmap = ({ scores, onStockClick }: HeatmapProps) => {
  const getScoreColor = (score: number): string => {
    if (score > 0.2) return 'bg-green-600';
    if (score > 0.1) return 'bg-green-500';
    if (score > 0) return 'bg-green-400';
    if (score === 0) return 'bg-gray-400';
    if (score > -0.1) return 'bg-red-400';
    if (score > -0.2) return 'bg-red-500';
    return 'bg-red-600';
  };

  const getScoreTextColor = (score: number): string => {
    return Math.abs(score) > 0.15 ? 'text-white' : 'text-gray-900';
  };

  return (
    <div className="grid grid-cols-10 gap-1">
      {scores.map((item, index) => (
        <div
          key={index}
          className={`
            ${getScoreColor(item.score)} 
            ${getScoreTextColor(item.score)}
            p-2 rounded cursor-pointer hover:opacity-80 transition-opacity
            min-h-[60px] flex flex-col justify-center items-center
          `}
          onClick={() => onStockClick(item.company.ticker)}
          title={`${item.company.ticker}: ${item.company.name}\nScore: ${item.score.toFixed(3)}\nArticles: ${item.article_count}`}
        >
          <div className="font-bold text-sm">{item.company.ticker}</div>
          <div className="text-xs">{item.score.toFixed(2)}</div>
        </div>
      ))}
    </div>
  );
};
