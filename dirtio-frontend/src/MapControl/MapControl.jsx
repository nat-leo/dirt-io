import { useEffect, useRef } from "react";

/**
 * MapControl wraps HTML elements and renders them as a Google Maps overlay.
 *
 * @param {google.maps.Map} map - The Google Maps instance
 * @param {google.maps.ControlPosition} position - Position on the map (e.g., TOP_RIGHT)
 * @param {React.ReactNode} children - JSX elements to render in the overlay
 */
export default function MapControl({ map, position = window.google.maps.ControlPosition.TOP_RIGHT, children }) {
  const containerRef = useRef(null);
  const rootRef = useRef(null);

  useEffect(() => {
    if (!map) return;

    // Create container only once
    if (!containerRef.current) {
      const containerDiv = document.createElement("div");
      map.controls[position].push(containerDiv);
      containerRef.current = containerDiv;

      // Create React root only once
      import("react-dom/client").then(({ createRoot }) => {
        rootRef.current = createRoot(containerDiv);
        rootRef.current.render(children);
      });
    } else if (rootRef.current) {
      // Update existing root
      rootRef.current.render(children);
    }

    // Cleanup on unmount
    return () => {
      if (containerRef.current) {
        const index = map.controls[position].getArray().indexOf(containerRef.current);
        if (index > -1) map.controls[position].removeAt(index);
        containerRef.current = null;
        rootRef.current = null;
      }
    };
  }, [map, position, children]);

  return null;
}
