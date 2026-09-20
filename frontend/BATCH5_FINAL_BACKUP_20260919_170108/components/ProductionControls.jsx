import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ArrowUp, HelpCircle, X } from "lucide-react";

export function ProductionControls() {
  const [cookies, setCookies] = useState(() => localStorage.getItem("n1mox30_cookie_choice") || "");
  const [top, setTop] = useState(false);

  useEffect(() => {
    const onScroll = () => setTop(window.scrollY > 700);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const choose = (value) => { localStorage.setItem("n1mox30_cookie_choice", value); setCookies(value); };

  return <>
    <a className="nm-skip" href="#main-content">Skip to content</a>
    <Link className="nm-help-float" to="/help" aria-label="Open N1MOX30 Help Center"><HelpCircle size={20}/><span>Help</span></Link>
    {top && <button className="nm-top-button" onClick={() => window.scrollTo({top:0,behavior:"smooth"})} aria-label="Back to top"><ArrowUp size={18}/></button>}
    {!cookies && <div className="nm-cookie" role="dialog" aria-label="Cookie preferences">
      <div><strong>Privacy choices</strong><p>We use essential storage to operate N1MOX30. Optional analytics should only be enabled where applicable consent is provided.</p></div>
      <div className="nm-cookie-actions"><button onClick={() => choose("necessary")}>Necessary only</button><button className="primary" onClick={() => choose("all")}>Allow optional</button><Link to="/cookies">Learn more</Link><button aria-label="Close cookie notice" onClick={() => choose("necessary")}><X size={16}/></button></div>
    </div>}
  </>;
}