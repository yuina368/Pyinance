import React, { useState, useEffect } from 'react';
import { Search as SearchIcon } from 'lucide-react';
import { apiService } from '../services/api';
import type { Company } from '../types';

interface SearchProps {
  onCompanySelect: (company: Company) => void;
}

export const Search: React.FC<SearchProps> = ({ onCompanySelect }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const searchCompanies = async () => {
      if (query.length < 2) {
        setResults([]);
        setShowResults(false);
        return;
      }

      try {
        setLoading(true);
        const companies = await apiService.getCompanies();
        const filtered = companies.filter(
          (company) =>
            company.ticker.toLowerCase().includes(query.toLowerCase()) ||
            company.name.toLowerCase().includes(query.toLowerCase())
        );
        setResults(filtered);
        setShowResults(true);
      } catch (error) {
        console.error('Failed to search companies:', error);
      } finally {
        setLoading(false);
      }
    };

    const debounceTimer = setTimeout(searchCompanies, 300);
    return () => clearTimeout(debounceTimer);
  }, [query]);

  const handleSelect = (company: Company) => {
    onCompanySelect(company);
    setQuery('');
    setResults([]);
    setShowResults(false);
  };

  return (
    <div className="relative">
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies by ticker or name..."
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {showResults && results.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-600">Loading...</div>
          ) : (
            results.map((company) => (
              <div
                key={company.id}
                onClick={() => handleSelect(company)}
                className="p-3 hover:bg-gray-100 cursor-pointer border-b border-gray-200 last:border-b-0"
              >
                <div className="font-semibold">{company.ticker}</div>
                <div className="text-sm text-gray-600">{company.name}</div>
              </div>
            ))
          )}
        </div>
      )}

      {showResults && !loading && results.length === 0 && query.length >= 2 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4 text-center text-gray-600">
          No companies found
        </div>
      )}
    </div>
  );
};
