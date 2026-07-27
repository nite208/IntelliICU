import { useEffect, useRef } from "react";

export default function DNAHelixCanvas({ className = "" }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;

    let width = (canvas.width = canvas.offsetWidth);
    let height = (canvas.height = canvas.offsetHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
    };

    window.addEventListener("resize", handleResize);

    // DNA Helix Parameters
    const numPoints = 70;
    const radius = Math.min(width, height) * 0.18;
    const helixLength = height * 1.1;
    let angleOffset = 0;

    // Ambient floating particles
    const ambientCount = 45;
    const ambientParticles = Array.from({ length: ambientCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 2 + 0.5,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.5 + 0.2,
    }));

    const render = () => {
      ctx.clearRect(0, 0, width, height);

      // Render Ambient Floating Gold Particles
      ambientParticles.forEach((p) => {
        p.x += p.speedX;
        p.y += p.speedY;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(234, 179, 8, ${p.alpha * 0.6})`;
        ctx.shadowBlur = 8;
        ctx.shadowColor = "#eab308";
        ctx.fill();
      });

      // Render DNA Double Helix
      angleOffset += 0.012;
      const centerX = width * 0.72;
      const startY = -height * 0.05;

      const strand1 = [];
      const strand2 = [];

      for (let i = 0; i < numPoints; i++) {
        const progress = i / numPoints;
        const y = startY + progress * helixLength;
        const angle = progress * Math.PI * 5 + angleOffset;

        const x1 = centerX + Math.cos(angle) * radius;
        const z1 = Math.sin(angle); // Depth factor -1 to 1

        const x2 = centerX + Math.cos(angle + Math.PI) * radius;
        const z2 = Math.sin(angle + Math.PI);

        strand1.push({ x: x1, y, z: z1, angle });
        strand2.push({ x: x2, y, z: z2, angle: angle + Math.PI });
      }

      // Sort base-pair connections by depth for realistic rendering
      for (let i = 0; i < numPoints; i += 2) {
        const p1 = strand1[i];
        const p2 = strand2[i];
        const avgZ = (p1.z + p2.z) / 2;
        const alpha = Math.max(0.08, (avgZ + 1.2) / 2.4) * 0.45;

        // Draw connecting rungs (base pairs)
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = `rgba(245, 158, 11, ${alpha})`;
        ctx.lineWidth = 1.2;
        ctx.shadowBlur = 6;
        ctx.shadowColor = "#f59e0b";
        ctx.stroke();

        // Nucleotide node midpoint glow
        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        ctx.beginPath();
        ctx.arc(midX, midY, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(56, 189, 248, ${alpha * 0.8})`;
        ctx.fill();
      }

      // Draw Strand 1 Nodes
      strand1.forEach((p) => {
        const scale = (p.z + 1.5) / 2.5; // 0.2 to 1.0
        const nodeSize = Math.max(1.2, scale * 3.5);
        const alpha = Math.max(0.2, scale);

        ctx.beginPath();
        ctx.arc(p.x, p.y, nodeSize, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(234, 179, 8, ${alpha})`;
        ctx.shadowBlur = scale * 12;
        ctx.shadowColor = "#fbbf24";
        ctx.fill();
      });

      // Draw Strand 2 Nodes
      strand2.forEach((p) => {
        const scale = (p.z + 1.5) / 2.5;
        const nodeSize = Math.max(1.2, scale * 3.5);
        const alpha = Math.max(0.2, scale);

        ctx.beginPath();
        ctx.arc(p.x, p.y, nodeSize, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(14, 165, 233, ${alpha})`;
        ctx.shadowBlur = scale * 12;
        ctx.shadowColor = "#38bdf8";
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 w-full h-full pointer-events-none ${className}`}
    />
  );
}
