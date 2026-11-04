// Handler genérico para as páginas de superfície: lê o <form>, envia JSON
// para o endpoint da rota e mostra a resposta. Propositalmente simples — sem
// framework, sem sanitização extra além da que cada rota decidir fazer.
function initSurfaceForm(formId, endpoint, outputId, opts) {
  opts = opts || {};
  const form = document.getElementById(formId);
  const output = document.getElementById(outputId);
  const rendered = opts.renderedId ? document.getElementById(opts.renderedId) : null;

  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const data = {};
    new FormData(form).forEach((value, key) => { data[key] = value; });
    output.textContent = "Consultando o modelo local (Ollama)...";
    if (rendered) rendered.innerHTML = "";
    try {
      const resp = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const json = await resp.json();
      output.textContent = JSON.stringify(json, null, 2);
      // VULN (demo LLM05 — Tratamento inadequado da saída): a página de chat
      // injeta a saída do modelo como HTML sem escapar, de propósito, para
      // que a turma veja um XSS armazenado/refletido local e discuta a
      // mitigação (sempre tratar saída de LLM como dado, nunca como marcação
      // de confiança). Isso só acontece quando a própria página pede
      // opts.renderRaw — nenhuma outra rota usa essa opção.
      if (rendered && opts.renderRaw && json[opts.renderRaw] !== undefined) {
        rendered.innerHTML = json[opts.renderRaw];
      }
    } catch (err) {
      output.textContent = "Erro de rede: " + err;
    }
  });
}
