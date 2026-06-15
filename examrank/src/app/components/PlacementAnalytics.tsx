"use client";

import React, { useState, useMemo } from 'react';
import { College } from '@/lib/api';
import { motion } from 'framer-motion';
import { 
  Briefcase, 
  IndianRupee, 
  TrendingUp, 
  Award, 
  MapPin, 
  Home, 
  TerminalSquare 
} from 'lucide-react';

interface Props {
  colleges: College[];
}

export default function PlacementAnalytics({ colleges }: Props) {
  const [view, setView] = useState<'roi' | 'packages'>('roi');

  // Filter colleges that have placement data
  const data = useMemo(() => {
    return colleges.filter(c => c.avg_lpa && c.fees_lpa);
  }, [colleges]);

  const sortedData = useMemo(() => {
    if (view === 'roi') {
      return [...data].sort((a, b) => (b.roi_index || 0) - (a.roi_index || 0));
    } else {
      return [...data].sort((a, b) => (b.avg_lpa || 0) - (a.avg_lpa || 0));
    }
  }, [data, view]);

  if (colleges.length === 0) return null;
  if (data.length === 0) {
    return (
      <div className="w-full bg-white/5 border border-white/10 rounded-2xl p-6 text-center text-gray-400">
        <Briefcase className="w-8 h-8 mx-auto mb-3 opacity-50" />
        <p>No placement data available for the predicted colleges.</p>
      </div>
    );
  }

  // Get top 3 for the podium
  const top3 = sortedData.slice(0, 3);
  const others = sortedData.slice(3, 10); // show next 7

  return (
    <div className="w-full bg-white shadow-xl border border-primary-200/80 rounded-3xl p-6 md:p-8 mt-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h2 className="text-2xl font-bold text-primary-900 flex items-center gap-2">
            <TrendingUp className="text-emerald-500" />
            Placement & ROI Analytics
          </h2>
          <p className="text-primary-600 mt-1">
            Compare Average Packages vs Total Course Fees to find the best value for money.
          </p>
        </div>
        
        <div className="bg-primary-50 p-1 rounded-xl flex border border-primary-100">
          <button 
            onClick={() => setView('roi')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${view === 'roi' ? 'bg-emerald-500 text-white shadow-md' : 'text-primary-600 hover:text-primary-900 hover:bg-primary-100/50'}`}
          >
            Best ROI
          </button>
          <button 
            onClick={() => setView('packages')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${view === 'packages' ? 'bg-blue-500 text-white shadow-md' : 'text-primary-600 hover:text-primary-900 hover:bg-primary-100/50'}`}
          >
            Highest Packages
          </button>
        </div>
      </div>

      {/* Top 3 Podium */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 items-end">
        {[top3[1], top3[0], top3[2]].map((college, idx) => {
          if (!college) return null;
          // 0 is silver (2nd), 1 is gold (1st), 2 is bronze (3rd)
          const isFirst = idx === 1;
          const isSecond = idx === 0;
          const rank = isFirst ? 1 : isSecond ? 2 : 3;
          
          return (
            <motion.div 
              key={college.name + rank}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`relative rounded-2xl p-6 border ${
                isFirst 
                  ? 'bg-gradient-to-b from-amber-50 to-white border-amber-300 md:-mt-8 shadow-lg' 
                  : isSecond
                    ? 'bg-gradient-to-b from-primary-50 to-white border-primary-300 shadow'
                    : 'bg-gradient-to-b from-orange-50 to-white border-orange-300 shadow'
              }`}
            >
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full flex items-center justify-center font-bold text-white shadow-lg"
                   style={{ background: isFirst ? '#f59e0b' : isSecond ? '#94a3b8' : '#d97706' }}>
                {rank}
              </div>
              
              <h3 className="text-lg font-bold text-primary-900 text-center mt-2 mb-1 line-clamp-1" title={college.name}>
                {college.name}
              </h3>
              <p className="text-xs text-center text-primary-500 mb-4">{college.branch}</p>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center bg-primary-50 p-3 rounded-xl border border-primary-100/50">
                  <div className="text-xs font-semibold text-primary-600">Avg Package</div>
                  <div className="font-bold text-success-600 flex items-center">
                    <IndianRupee className="w-3 h-3 mr-1" />
                    {college.avg_lpa} LPA
                  </div>
                </div>
                
                <div className="flex justify-between items-center bg-primary-50 p-3 rounded-xl border border-primary-100/50">
                  <div className="text-xs font-semibold text-primary-600">Total Fees</div>
                  <div className="font-bold text-danger-500 flex items-center">
                    <IndianRupee className="w-3 h-3 mr-1" />
                    {college.fees_lpa} L
                  </div>
                </div>
                
                <div className="flex justify-between items-center bg-primary-100 p-3 rounded-xl border border-primary-200">
                  <div className="text-xs font-bold text-primary-700">ROI Index</div>
                  <div className="font-bold text-primary-900 text-lg">{college.roi_index}x</div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* List view for the rest */}
      {others.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-xs text-primary-600 uppercase tracking-wider border-b border-primary-200 bg-primary-50/50">
                <th className="py-3 pl-4 font-bold rounded-tl-xl">Rank</th>
                <th className="py-3 font-bold">College & Branch</th>
                <th className="py-3 font-bold text-right">Avg Package</th>
                <th className="py-3 font-bold text-right">Total Fees</th>
                <th className="py-3 pr-4 font-bold text-right rounded-tr-xl">ROI Index</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-primary-100">
              {others.map((college, i) => (
                <tr key={i} className="hover:bg-primary-50 transition-colors">
                  <td className="py-4 pl-4 text-primary-500 font-bold">#{i + 4}</td>
                  <td className="py-4">
                    <div className="font-bold text-primary-900">{college.name}</div>
                    <div className="text-xs text-primary-600 flex gap-2 items-center mt-1 font-medium">
                      <span>{college.branch}</span>
                      {college.coding_culture && (
                        <span className="flex items-center gap-1 text-info-600 bg-info-50 px-2 py-0.5 rounded-full border border-info-200/50">
                          <TerminalSquare className="w-3 h-3" />
                          Good Coding Culture
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="py-4 text-right font-bold text-success-600">₹{college.avg_lpa} L</td>
                  <td className="py-4 text-right font-bold text-danger-500">₹{college.fees_lpa} L</td>
                  <td className="py-4 pr-4 text-right font-bold text-primary-900">{college.roi_index}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
