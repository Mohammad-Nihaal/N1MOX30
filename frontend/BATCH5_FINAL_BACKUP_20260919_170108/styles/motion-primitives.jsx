import { useEffect, useRef, useState } from "react";

export function useReducedMotion() {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(media.matches);
    update();
    media.addEventListener?.("change", update);
    return () => media.removeEventListener?.("change", update);
  }, []);
  return reduced;
}

export function PageTransition({ children, className = "" }) {
  return <div className={`nm-page-enter ${className}`}>{children}</div>;
}

export function Reveal({ children, className = "", delay = 0 }) {
  const reduced = useReducedMotion();
  return (
    <div
      className={`nm-fade-up ${className}`}
      style={reduced ? undefined : { animationDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

export function useCountUp(value, duration = 650) {
  const target = Number(value) || 0;
  const [display, setDisplay] = useState(target);
  const previous = useRef(target);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setDisplay(target);
      previous.current = target;
      return;
    }

    const start = performance.now();
    const from = previous.current;

    let frame = 0;
    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(from + (target - from) * eased);
      if (progress < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    previous.current = target;
    return () => cancelAnimationFrame(frame);
  }, [target, duration]);

  return display;
}
