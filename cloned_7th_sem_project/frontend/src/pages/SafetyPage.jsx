import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  PhoneCall, 
  CheckCircle2, 
  AlertOctagon, 
  Copy, 
  Check, 
  Phone,
  Package,
  Home,
  Navigation,
  LifeBuoy
} from 'lucide-react';
import { ShieldWaves } from '../components/Icons';

export default function SafetyPage() {
  const [safetyData, setSafetyData] = useState(null);
  const [checkedItems, setCheckedItems] = useState({});
  const [copiedNumber, setCopiedNumber] = useState(null);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/safety-data')
      .then((res) => res.json())
      .then((data) => setSafetyData(data))
      .catch((err) => console.error('Failed to load safety data:', err));
  }, []);

  const toggleCheck = (idxKey) => {
    setCheckedItems((prev) => ({
      ...prev,
      [idxKey]: !prev[idxKey]
    }));
  };

  const handleCopy = (num) => {
    navigator.clipboard.writeText(num);
    setCopiedNumber(num);
    setTimeout(() => setCopiedNumber(null), 2000);
  };

  if (!safetyData) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
        <p>Loading Safety Guidelines &amp; Emergency Directory...</p>
      </div>
    );
  }

  const { helplines, checklists, rules } = safetyData;

  // Total checklist count & completed count
  const allChecklistItems = Object.values(checklists).flat();
  const totalItems = allChecklistItems.length;
  const completedItems = Object.values(checkedItems).filter(Boolean).length;
  const progressPct = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;

  const getCategoryIcon = (category) => {
    if (category.includes('Emergency Kit')) return <Package size={16} color="#0f172a" />;
    if (category.includes('Home Protection')) return <Home size={16} color="#0f172a" />;
    return <Navigation size={16} color="#0f172a" />;
  };

  return (
    <div className="page-container">
      {/* Page Header with Sophisticated Black & White Shield and Waves Emblem */}
      <div className="section-header" style={{ marginTop: '4px' }}>
        <div className="section-icon" style={{ background: '#0f172a', color: '#ffffff' }}>
          <ShieldWaves size={24} color="#0f172a" waveColor="#ffffff" />
        </div>
        <div>
          <div className="section-title">Emergency Helplines &amp; Disaster Safety Center</div>
          <div className="section-sub">Immediate 24×7 contact numbers, interactive survival checklists, and life-safety guidelines</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 5fr) minmax(0, 5fr)', gap: '24px' }}>
        {/* ── LEFT COLUMN: Important Contact Numbers ── */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div className="white-card-title" style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a', margin: 0 }}>
              Important Emergency Helplines (24×7)
            </div>
            <span style={{ fontSize: '11px', background: '#dcfce7', color: '#16a34a', padding: '4px 10px', borderRadius: '12px', fontWeight: 800 }}>
              TOLL-FREE &amp; ACTIVE
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {helplines.map((hl, i) => (
              <div key={i} className="helpline-card" style={{ margin: 0, justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  {/* Clean Monochrome Badge with Lucide Icon */}
                  <div style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: '10px',
                    background: '#0f172a',
                    color: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    <Phone size={18} />
                  </div>
                  <div>
                    <div className="helpline-name">{hl.name}</div>
                    <div className="helpline-num" style={{ color: '#0f172a', fontWeight: 900 }}>
                      {hl.number}
                    </div>
                    <div className="helpline-desc">{hl.desc}</div>
                  </div>
                </div>

                {/* Quick Call & Copy Actions */}
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <button
                    onClick={() => handleCopy(hl.number)}
                    title="Copy Number"
                    style={{
                      background: '#f8fafc',
                      border: '1px solid #cbd5e1',
                      borderRadius: '8px',
                      padding: '8px',
                      cursor: 'pointer',
                      color: copiedNumber === hl.number ? '#16a34a' : '#64748b'
                    }}
                  >
                    {copiedNumber === hl.number ? <Check size={15} /> : <Copy size={15} />}
                  </button>
                  <a
                    href={`tel:${hl.number.replace(/[^0-9]/g, '')}`}
                    style={{
                      background: '#0f172a',
                      color: '#ffffff',
                      textDecoration: 'none',
                      padding: '8px 14px',
                      borderRadius: '8px',
                      fontSize: '12px',
                      fontWeight: 800,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px'
                    }}
                  >
                    <PhoneCall size={13} />
                    Call
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── RIGHT COLUMN: Interactive Flood Checklist ── */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
            <div className="white-card-title" style={{ fontSize: '16px', fontWeight: 800, color: '#0f172a', margin: 0 }}>
              Flood Preparedness Checklist
            </div>
            <div style={{ fontSize: '12px', fontWeight: 800, color: progressPct === 100 ? '#16a34a' : '#0f172a' }}>
              {completedItems} / {totalItems} Ready ({progressPct}%)
            </div>
          </div>

          {/* Progress Bar (Color changes to green upon 100% completion) */}
          <div style={{ background: '#e2e8f0', height: '8px', borderRadius: '4px', overflow: 'hidden', marginBottom: '16px' }}>
            <div style={{ width: `${progressPct}%`, height: '100%', background: progressPct === 100 ? '#16a34a' : '#0f172a', transition: 'width 0.3s ease' }} />
          </div>

          <div style={{ background: '#f8fafc', borderLeft: '4px solid #0f172a', padding: '12px 18px', borderRadius: '0 8px 8px 0', marginBottom: '18px', fontSize: '12.5px', color: '#1e293b' }}>
            <b>Preparedness Protocol:</b> Verify each checklist item to safeguard lives and vital assets prior to severe flood cresting.
          </div>

          {Object.entries(checklists).map(([category, items], catIdx) => (
            <div key={category} style={{ marginBottom: '18px' }}>
              <div style={{ fontSize: '14px', fontWeight: 800, color: '#0f172a', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                {getCategoryIcon(category)}
                <span>{category.replace(/[^\w\s]/gi, '').trim()}</span>
              </div>
              <div className="white-card" style={{ padding: '6px 20px', margin: 0 }}>
                {items.map((item, itemIdx) => {
                  const itemKey = `${catIdx}-${itemIdx}`;
                  const isChecked = !!checkedItems[itemKey];

                  return (
                    <div 
                      key={itemIdx} 
                      className="checklist-item" 
                      onClick={() => toggleCheck(itemKey)}
                      style={{ cursor: 'pointer', userSelect: 'none' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', marginRight: '6px' }}>
                        {isChecked ? (
                          <CheckCircle2 size={19} color="#16a34a" />
                        ) : (
                          <div style={{ width: '18px', height: '18px', border: '2px solid #cbd5e1', borderRadius: '4px' }} />
                        )}
                      </div>
                      <div className="checklist-text" style={{ textDecoration: isChecked ? 'line-through' : 'none', opacity: isChecked ? 0.6 : 1 }}>
                        <span className="checklist-bold">{item.bold}:</span> {item.text}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

          {/* Critical Flood Survival Box */}
          <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', borderRadius: '14px', padding: '22px 26px', color: '#ffffff', marginTop: '20px', boxShadow: '0 4px 15px rgba(15, 23, 42, 0.2)' }}>
            <div style={{ fontSize: '15px', fontWeight: 900, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertOctagon size={19} color="#60a5fa" />
              Critical Survival Protocols During Flooding
            </div>
            <div style={{ fontSize: '13px', lineHeight: 2, opacity: 0.95 }}>
              {rules.map((r, i) => (
                <div key={i}>• {r}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
