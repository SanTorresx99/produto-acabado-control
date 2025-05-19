document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("filtros-form");
  const tbody = document.querySelector("#ops-table tbody");
  const cardsContainer = document.getElementById("resumo-cards");

  const formatarDataBR = (dataStr) => {
    const [ano, mes, dia] = dataStr.split("-");
    return `${dia}/${mes}/${ano}`;
  };

  const formatarDataUSA = (dataStr) => {
    const [dia, mes, ano] = dataStr.split("/");
    return `${ano}-${mes}-${dia}`;
  };

  const dataInicioInput = document.getElementById("data-inicio");
  const dataFimInput = document.getElementById("data-fim");

  if (dataInicioInput && dataFimInput) {
    const hoje = new Date();
    const inicioMes = new Date(hoje.getFullYear(), hoje.getMonth(), 1);

    const formatarParaInput = (date) => {
      const d = String(date.getDate()).padStart(2, "0");
      const m = String(date.getMonth() + 1).padStart(2, "0");
      const y = date.getFullYear();
      return `${d}/${m}/${y}`;
    };

    dataInicioInput.value = formatarParaInput(inicioMes);
    dataFimInput.value = formatarParaInput(hoje);

    flatpickr("#data-inicio", { dateFormat: "d/m/Y", locale: "pt" });
    flatpickr("#data-fim", { dateFormat: "d/m/Y", locale: "pt" });
  }

  if (form) {
    form.addEventListener("submit", async function (event) {
      event.preventDefault();

      const dataInicio = dataInicioInput.value;
      const dataFim = dataFimInput.value;
      const dInicio = new Date(formatarDataUSA(dataInicio));
      const dFim = new Date(formatarDataUSA(dataFim));

      if (dInicio > dFim) {
        alert("A data de início não pode ser posterior à data de fim.");
        return;
      }

      await buscarDados();
    });
  }

  function ordenarOps(ops) {
    const prioridade = {
      "⚠️ Registro a maior": 1,
      "✅ Registro OK": 2,
      "✅ Registrando": 3,
      "🔴 Pendente": 4
    };

    return ops.sort((a, b) => {
      const p1 = prioridade[a.STATUS] || 9;
      const p2 = prioridade[b.STATUS] || 9;
      if (p1 !== p2) return p1 - p2;

      const sub1 = (a.SUB_ESPECIE || "").toUpperCase();
      const sub2 = (b.SUB_ESPECIE || "").toUpperCase();
      if (sub1 < sub2) return -1;
      if (sub1 > sub2) return 1;

      const id1 = parseInt(a.ID_PRODUTO || 0);
      const id2 = parseInt(b.ID_PRODUTO || 0);
      return id1 - id2;
    });
  }

  async function buscarDados() {
    const dataInicio = formatarDataUSA(document.getElementById("data-inicio").value);
    const dataFim = formatarDataUSA(document.getElementById("data-fim").value);
    const subespecie = document.getElementById("subespecie").value;
    const idProduto = document.getElementById("id-produto").value;
    const codOp = document.getElementById("cod-op").value;
    const tipoLinha = document.getElementById("tipo-linha").checked;
    const tipoSob = document.getElementById("tipo-sob").checked;

    let tipoOp = "ambos";
    if (tipoLinha && !tipoSob) tipoOp = "linha";
    else if (!tipoLinha && tipoSob) tipoOp = "sob_encomenda";
    else if (!tipoLinha && !tipoSob) return alert("Selecione pelo menos um tipo de OP");

    try {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align: center">Carregando dados...</td></tr>';
      cardsContainer.innerHTML = '<div class="card">Carregando...</div>';

      const response = await fetch(
        `/api/ops?data_inicio=${formatarDataBR(dataInicio)}&data_fim=${formatarDataBR(dataFim)}&subespecie=${subespecie}&id_produto=${idProduto}&cod_op=${codOp}&tipo_op=${tipoOp}`
      );
      if (!response.ok) throw new Error(`Erro ${response.status}: ${response.statusText}`);

      const data = await response.json();
      const ordenado = ordenarOps(data.ops);
      renderizarTabela(ordenado);
      renderizarCards(calcularResumo(ordenado));
    } catch (error) {
      console.error("Erro ao buscar dados:", error);
      tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: #dc2626">Erro ao carregar dados: ${error.message}</td></tr>`;
      cardsContainer.innerHTML = `<div class="card" style="color: #dc2626">Erro: ${error.message}</div>`;
    }
  }

    function renderizarTabela(ops) {
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!ops || ops.length === 0) {
      tbody.innerHTML = '<tr><td colspan="9" style="text-align: center">Nenhum dado encontrado</td></tr>';
      return;
    }

    ops.forEach((op) => {
      const tr = document.createElement("tr");
      tr.onclick = () => window.location.href = `/op/${op.CODIGO_OP}`;

      const status = op.STATUS || "";
      let statusClass = "status-pendente";
      if (status.includes("Registro OK")) statusClass = "status-ok";
      else if (status.includes("Registrando")) statusClass = "status-parcial";
      else if (status.includes("a maior")) statusClass = "status-maior";

      const tipoIcone = op.TIPO_OP === "LIN_PROD" ? "🏭" : op.TIPO_OP === "SOB_ENC" ? "🪡" : "";

      tr.innerHTML = `
        <td class="${statusClass}">${status}</td>
        <td>${op.CODIGO_OP || ""}</td>
        <td>${op.ID_PRODUTO || ""}</td>
        <td>${op.NOME_PRODUTO || ""}</td>
        <td>${op.ESPECIE || ""}</td>
        <td>${op.SUB_ESPECIE || ""}</td>
        <td>${op.QTD_PREVISTA || 0}</td>
        <td>${op.QTD_REGISTRADA || 0}</td>
        <td>${tipoIcone}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function calcularResumo(ops) {
    const resumo = {};
    if (!ops || ops.length === 0) return resumo;

    ops.forEach((op) => {
      const especie = op.ESPECIE || "Não especificado";
      if (!resumo[especie]) resumo[especie] = { qtd_prevista: 0, qtd_registrada: 0 };
      resumo[especie].qtd_prevista += Number(op.QTD_PREVISTA || 0);
      resumo[especie].qtd_registrada += Number(op.QTD_REGISTRADA || 0);
    });

    return resumo;
  }

  function renderizarCards(resumo) {
    cardsContainer.innerHTML = "";
    if (Object.keys(resumo).length === 0) {
      cardsContainer.innerHTML = '<div class="card">Sem dados para exibir</div>';
      return;
    }

    for (const especie in resumo) {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <strong>${especie}</strong>
        <p>Qtd Prevista: ${resumo[especie].qtd_prevista}</p>
        <p>Qtd Registrada: ${resumo[especie].qtd_registrada}</p>
      `;
      cardsContainer.appendChild(card);
    }

    const totalPrevisto = Object.values(resumo).reduce((acc, r) => acc + r.qtd_prevista, 0);
    const totalRegistrado = Object.values(resumo).reduce((acc, r) => acc + r.qtd_registrada, 0);

    const totalCard = document.createElement("div");
    totalCard.className = "card";
    totalCard.style.backgroundColor = "#f0f9ff";
    totalCard.style.borderColor = "#3b82f6";
    totalCard.innerHTML = `
      <strong>TOTAL GERAL</strong>
      <p>Qtd Prevista: ${totalPrevisto}</p>
      <p>Qtd Registrada: ${totalRegistrado}</p>
    `;
    cardsContainer.appendChild(totalCard);
  }

  async function carregarSubespecies() {
    const select = document.getElementById("subespecie");
    if (!select) return;

    const dataInicio = formatarDataUSA(document.getElementById("data-inicio").value);
    const dataFim = formatarDataUSA(document.getElementById("data-fim").value);

    const response = await fetch(`/api/filtros?data_inicio=${formatarDataBR(dataInicio)}&data_fim=${formatarDataBR(dataFim)}`);
    const data = await response.json();

    while (select.options.length > 1) select.remove(1);
    data.subespecies?.forEach((sub) => {
      const opt = document.createElement("option");
      opt.value = sub;
      opt.textContent = sub;
      select.appendChild(opt);
    });
  }

  if (dataInicioInput && dataFimInput) {
    dataInicioInput.addEventListener("change", carregarSubespecies);
    dataFimInput.addEventListener("change", carregarSubespecies);
    carregarSubespecies();
    buscarDados();
  }

});

