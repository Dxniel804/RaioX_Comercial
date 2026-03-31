/* script.js — partículas flutuantes leves */
(function () {
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');

  let W, H, particles = [];
  const COUNT = 38;
  const ACCENT = { r: 200, g: 169, b: 110 };

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function rand(min, max) { return Math.random() * (max - min) + min; }

  function Particle() {
    this.reset = function () {
      this.x    = rand(0, W);
      this.y    = rand(0, H);
      this.r    = rand(1, 2.8);
      this.vx   = rand(-.18, .18);
      this.vy   = rand(-.28, -.06);
      this.life = rand(0, 1);
      this.maxL = rand(.4, 1);
      this.grow = true;
      this.speed = rand(.003, .007);
    };
    this.reset();
  }

  for (let i = 0; i < COUNT; i++) particles.push(new Particle());

  function draw() {
    ctx.clearRect(0, 0, W, H);

    particles.forEach(p => {
      // opacidade que pulsa
      if (p.grow) { p.life += p.speed; if (p.life >= p.maxL) p.grow = false; }
      else         { p.life -= p.speed; if (p.life <= 0)      p.reset(); }

      const alpha = Math.max(0, Math.min(p.life * .7, .7));

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${ACCENT.r},${ACCENT.g},${ACCENT.b},${alpha})`;
      ctx.fill();

      p.x += p.vx;
      p.y += p.vy;

      // Rebobina quando sai da tela
      if (p.y < -10)  { p.y = H + 10; }
      if (p.x < -10)  { p.x = W + 10; }
      if (p.x > W+10) { p.x = -10; }
    });

    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  draw();
})();