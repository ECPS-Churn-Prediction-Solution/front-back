import React, { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { track } from './analytics.js';

const RouteTracker = () => {
  const location = useLocation();
  const prevPathRef = useRef(null);

  useEffect(() => {
    const fromPath = prevPathRef.current || (document.referrer || undefined);
    const toPath = location.pathname + (location.search || '');
    track('page_view', { from_path: fromPath, to_path: toPath });
    prevPathRef.current = toPath;
  }, [location]);

  return null;
};

export default RouteTracker;


