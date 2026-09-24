import { useState } from "react";
import { Link } from "react-router-dom";

export default function CookieConsent() {
  const [visible,setVisible]=useState(()=>localStorage.getItem("n1mox-cookie-consent")==="pending" || !localStorage.getItem("n1mox-cookie-consent"));
  if(!visible) return null;
  const choose=value=>{localStorage.setItem("n1mox-cookie-consent",value);setVisible(false);};
  return <div className="cookie-consent" role="dialog" aria-label="Cookie preferences"><div><strong>Cookies & privacy</strong><p>N1MOX30 uses necessary storage for authentication and preferences. Optional analytics should only activate after consent where required.</p><Link to="/cookies">Cookie policy</Link></div><div className="cookie-actions"><button onClick={()=>choose("rejected")}>Reject non-essential</button><button onClick={()=>choose("accepted")}>Accept</button><button onClick={()=>choose("preferences")}>Preferences</button></div></div>;
}
