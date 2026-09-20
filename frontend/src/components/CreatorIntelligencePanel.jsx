import { useState, useEffect } from "react";
import { getCreatorDashboard } from "../api/creatorDashboard";

export default function CreatorIntelligencePanel({
  userId,
}) {
  const [data,setData]=useState(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");

  useEffect(()=>{
    if(!userId){
      setLoading(false);
      return;
    }

    let active=true;

    getCreatorDashboard(userId)
      .then(result=>{
        if(active){
          setData(result);
        }
      })
      .catch(err=>{
        if(active){
          setError(err.message || "Unable to load creator data.");
        }
      })
      .finally(()=>{
        if(active){
          setLoading(false);
        }
      });

    return ()=>{
      active=false;
    };
  },[userId]);

  if(loading){
    return (
      <div className="nx-panel" style={{
        padding:20,
        borderRadius:20,
      }}>
        Loading creator intelligence...
      </div>
    );
  }

  if(error){
    return (
      <div className="nx-panel" style={{
        padding:20,
        borderRadius:20,
      }}>
        {error}
      </div>
    );
  }

  if(!data){
    return null;
  }

  if(data.status==="authorization_required"){
    return (
      <div className="nx-panel" style={{
        padding:20,
        borderRadius:20,
      }}>
        <div className="nx-section-title">
          Connect YouTube
        </div>
        <div className="nx-section-sub">
          Connect a creator account to unlock live
          channel analytics and growth intelligence.
        </div>
      </div>
    );
  }

  const summary=data.summary || {};
  const growth=data.growth || {};

  return (
    <div className="nx-grid nx-grid-4">

      <div className="nx-stat">
        <div className="nx-stat-label">
          TOTAL VIEWS
        </div>
        <div className="nx-stat-value">
          {Number(summary.total_views || 0).toLocaleString()}
        </div>
        <div className="nx-stat-meta">
          Live channel data
        </div>
      </div>

      <div className="nx-stat">
        <div className="nx-stat-label">
          ENGAGEMENT
        </div>
        <div className="nx-stat-value">
          {Number(
            summary.engagement_rate || 0
          ).toFixed(2)}%
        </div>
        <div className="nx-stat-meta">
          Likes + comments
        </div>
      </div>

      <div className="nx-stat">
        <div className="nx-stat-label">
          GROWTH SCORE
        </div>
        <div className="nx-stat-value">
          {Number(
            growth.growth_score || 0
          ).toFixed(0)}
        </div>
        <div className="nx-stat-meta">
          Intelligence engine
        </div>
      </div>

      <div className="nx-stat">
        <div className="nx-stat-label">
          VIDEOS ANALYZED
        </div>
        <div className="nx-stat-value">
          {summary.videos_analyzed || 0}
        </div>
        <div className="nx-stat-meta">
          Recent content
        </div>
      </div>

    </div>
  );
}