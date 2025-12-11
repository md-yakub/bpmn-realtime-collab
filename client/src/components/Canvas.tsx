export function Canvas({ containerRef }: any) {
  return (
    <div className="canvas-container">
      <div ref={containerRef} className="bpmn-canvas" />
    </div>
  );
}
