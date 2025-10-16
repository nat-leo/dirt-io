// HelloWorldButton.jsx
import { useEffect } from "react";

export default function HelloWorldButton({ map, position = window.google.maps.ControlPosition.TOP_LEFT }) {
  useEffect(() => {
    if (!map) return;

    // Create the button
    const controlDiv = document.createElement("div");
    controlDiv.style.backgroundColor = "#fff";
    controlDiv.style.border = "2px solid #fff";
    controlDiv.style.borderRadius = "3px";
    controlDiv.style.boxShadow = "0 2px 6px rgba(0,0,0,.3)";
    controlDiv.style.cursor = "pointer";
    controlDiv.style.margin = "10px";
    controlDiv.style.textAlign = "center";
    controlDiv.style.padding = "6px 12px";
    controlDiv.innerText = "Hello World";

    // Click event
    const handleClick = () => alert("Hello World!");
    controlDiv.addEventListener("click", handleClick);

    // Add to map controls
    map.controls[position].push(controlDiv);

    // Cleanup on unmount
    return () => {
      controlDiv.removeEventListener("click", handleClick);
      // Remove control from map
      const controlsArray = map.controls[position].getArray();
      const index = controlsArray.indexOf(controlDiv);
      if (index > -1) controlsArray.splice(index, 1);
    };
  }, [map, position]);

  return null; // nothing rendered in React DOM
}
