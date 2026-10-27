/*!
 * consentimento.js — gerenciador de consentimento de cookies (LGPD / Guia de Cookies da ANPD)
 * Parte da skill "blindagem-juridica". Sem dependências. Licença MIT.
 *
 * - Bloqueia scripts e iframes marcados com data-categoria-consentimento até o aceite.
 * - "Aceitar todos", "Rejeitar não essenciais" e "Preferências" no primeiro nível.
 * - Categorias granulares, reabertura por [data-abrir-preferencias-cookies], revogação.
 * - Google Consent Mode v2 (padrão "denied", atualizado conforme a escolha).
 * - Acessível: teclado, foco, role="dialog", aria-*.
 *
 * Uso: veja README.md nesta pasta.
 */
(function () {
  'use strict';

  var PADRAO = {
    versao: '1',                       // mude quando alterar categorias/fornecedores: pede novo consentimento
    validadeDias: 365,
    chave: 'blindagem_consentimento',
    urlPolitica: '/politica-de-privacidade',
    googleConsentMode: true,
    recarregarAoRevogar: true,
    textos: {
      titulo: 'Sua privacidade',
      descricao: 'Usamos cookies necessários para o site funcionar. Com a sua autorização, também usamos cookies de estatística, marketing e conteúdos de terceiros. Você pode mudar sua escolha quando quiser em "Preferências de cookies", no rodapé.',
      linkPolitica: 'Política de Privacidade',
      aceitarTodos: 'Aceitar todos',
      rejeitar: 'Rejeitar não essenciais',
      preferencias: 'Preferências',
      tituloPreferencias: 'Preferências de cookies',
      salvar: 'Salvar preferências',
      fechar: 'Fechar',
      sempreAtivo: 'Sempre ativo',
      conteudoBloqueado: 'Este conteúdo é fornecido por terceiros e pode usar cookies. Para vê-lo, autorize a categoria "{categoria}".',
      carregarConteudo: 'Autorizar e carregar'
    },
    categorias: [
      { id: 'necessarios', nome: 'Necessários', descricao: 'Essenciais para segurança, login, carrinho e para lembrar sua escolha sobre cookies. Não podem ser desativados.', obrigatoria: true },
      { id: 'estatistica', nome: 'Estatística', descricao: 'Ajudam a entender como o site é usado, de forma agregada, para melhorá-lo.' },
      { id: 'marketing', nome: 'Marketing', descricao: 'Medem campanhas e permitem exibir anúncios relevantes em outras plataformas.' },
      { id: 'funcionalidades', nome: 'Conteúdo de terceiros', descricao: 'Vídeos, mapas, chats e outros recursos incorporados de outros serviços.' }
    ]
  };

  var CONSENT_MODE = {
    estatistica: ['analytics_storage'],
    marketing: ['ad_storage', 'ad_user_data', 'ad_personalization'],
    funcionalidades: ['functionality_storage', 'personalization_storage']
  };
  var COOKIES_CONHECIDOS = {
    estatistica: [/^_ga/, /^_gid$/, /^_gat/, /^_hj/, /^_clck$/, /^_clsk$/, /^mp_/, /^amp_/, /^ph_/, /^_pk_/],
    marketing: [/^_fbp$/, /^_fbc$/, /^_gcl_/, /^_ttp$/, /^_tt_/, /^_uetsid$/, /^_uetvid$/, /^li_/, /^_pin_/, /^IDE$/]
  };

  var cfg = mesclar(PADRAO, window.blindagemConsentConfig || {});
  var estado = null;
  var banner = null;
  var painel = null;
  var focoAnterior = null;

  // ---------------------------------------------------------------- util
  function mesclar(a, b) {
    var r = {};
    var k;
    for (k in a) if (Object.prototype.hasOwnProperty.call(a, k)) r[k] = a[k];
    for (k in b) {
      if (!Object.prototype.hasOwnProperty.call(b, k)) continue;
      r[k] = (k === 'textos') ? mesclar(a.textos, b.textos) : b[k];
    }
    return r;
  }

  function el(tag, attrs, filhos) {
    var n = document.createElement(tag);
    attrs = attrs || {};
    for (var k in attrs) {
      if (!Object.prototype.hasOwnProperty.call(attrs, k)) continue;
      if (k === 'texto') n.textContent = attrs[k];
      else if (k === 'classe') n.className = attrs[k];
      else n.setAttribute(k, attrs[k]);
    }
    (filhos || []).forEach(function (f) { if (f) n.appendChild(f); });
    return n;
  }

  function ler() {
    var bruto = null;
    try { bruto = window.localStorage.getItem(cfg.chave); } catch (e) {
      var m = document.cookie.match(new RegExp('(?:^|; )' + cfg.chave + '=([^;]*)'));
      bruto = m ? decodeURIComponent(m[1]) : null;
    }
    if (!bruto) return null;
    try {
      var s = JSON.parse(bruto);
      var idadeDias = (Date.now() - new Date(s.data).getTime()) / 864e5;
      if (s.versao !== cfg.versao || !(idadeDias < cfg.validadeDias)) return null;
      return s;
    } catch (e) { return null; }
  }

  function gravar(s) {
    var bruto = JSON.stringify(s);
    try { window.localStorage.setItem(cfg.chave, bruto); } catch (e) {
      document.cookie = cfg.chave + '=' + encodeURIComponent(bruto) + '; max-age=' +
        (cfg.validadeDias * 86400) + '; path=/; SameSite=Lax';
    }
  }

  function apagarCookies(categoria) {
    var padroes = COOKIES_CONHECIDOS[categoria] || [];
    var host = window.location.hostname;
    var partes = host.split('.');
    var dominios = [host];
    for (var i = 1; i < partes.length - 1; i++) dominios.push('.' + partes.slice(i).join('.'));
    document.cookie.split('; ').forEach(function (par) {
      var nome = par.split('=')[0];
      if (!padroes.some(function (p) { return p.test(nome); })) return;
      dominios.concat(['']).forEach(function (d) {
        document.cookie = nome + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (d ? '; domain=' + d : '');
      });
    });
  }

  // -------------------------------------------------- Google Consent Mode
  function gtagSeguro() {
    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag !== 'function') {
      window.gtag = function () { window.dataLayer.push(arguments); };
    }
    return window.gtag;
  }

  function consentModeParams(categorias) {
    var p = {};
    Object.keys(CONSENT_MODE).forEach(function (cat) {
      CONSENT_MODE[cat].forEach(function (chave) {
        p[chave] = categorias && categorias[cat] ? 'granted' : 'denied';
      });
    });
    p.security_storage = 'granted';
    return p;
  }

  if (cfg.googleConsentMode) {
    var padraoCM = consentModeParams(null);
    padraoCM.wait_for_update = 500;
    gtagSeguro()('consent', 'default', padraoCM);
  }

  // ------------------------------------------- ativação de scripts/iframes
  function permitido(cat) {
    if (!cat || cat === 'necessarios') return true;
    return !!(estado && estado.categorias && estado.categorias[cat]);
  }

  function ativarScripts() {
    var lista = document.querySelectorAll('script[type="text/plain"][data-categoria-consentimento]:not([data-consentimento-ativado])');
    Array.prototype.forEach.call(lista, function (antigo) {
      if (!permitido(antigo.getAttribute('data-categoria-consentimento'))) return;
      var novo = document.createElement('script');
      Array.prototype.forEach.call(antigo.attributes, function (a) {
        if (a.name === 'type' || a.name === 'data-src') return;
        novo.setAttribute(a.name, a.value);
      });
      var tipo = antigo.getAttribute('data-type');
      if (tipo) novo.type = tipo;
      if (antigo.getAttribute('data-src')) novo.src = antigo.getAttribute('data-src');
      else novo.text = antigo.text;
      antigo.setAttribute('data-consentimento-ativado', '');
      antigo.parentNode.insertBefore(novo, antigo.nextSibling);
    });
  }

  function nomeCategoria(id) {
    var c = cfg.categorias.filter(function (x) { return x.id === id; })[0];
    return c ? c.nome : id;
  }

  function tratarIframes() {
    var lista = document.querySelectorAll('iframe[data-src][data-categoria-consentimento]');
    Array.prototype.forEach.call(lista, function (fr) {
      var cat = fr.getAttribute('data-categoria-consentimento');
      var aviso = fr.previousElementSibling && fr.previousElementSibling.hasAttribute('data-aviso-consentimento')
        ? fr.previousElementSibling : null;
      if (permitido(cat)) {
        if (!fr.getAttribute('src')) fr.setAttribute('src', fr.getAttribute('data-src'));
        fr.hidden = false;
        if (aviso) aviso.parentNode.removeChild(aviso);
        return;
      }
      fr.hidden = true;
      if (aviso) return;
      var botao = el('button', { type: 'button', classe: 'bc-botao bc-botao-primario', texto: cfg.textos.carregarConteudo });
      botao.addEventListener('click', function () {
        var cats = estado ? copiar(estado.categorias) : {};
        cats[cat] = true;
        salvar(cats);
      });
      aviso = el('div', { classe: 'bc-aviso-bloqueado', 'data-aviso-consentimento': '' }, [
        el('p', { texto: cfg.textos.conteudoBloqueado.replace('{categoria}', nomeCategoria(cat)) }),
        botao
      ]);
      fr.parentNode.insertBefore(aviso, fr);
    });
  }

  function copiar(o) { var r = {}; for (var k in o) r[k] = o[k]; return r; }

  function aplicar(anterior) {
    if (cfg.googleConsentMode) gtagSeguro()('consent', 'update', consentModeParams(estado.categorias));
    ativarScripts();
    tratarIframes();
    try {
      window.dispatchEvent(new CustomEvent('consentimento:atualizado', { detail: copiar(estado.categorias) }));
    } catch (e) { /* navegadores muito antigos */ }
    var revogou = anterior && Object.keys(anterior).some(function (k) {
      return anterior[k] && !estado.categorias[k];
    });
    if (revogou) {
      Object.keys(anterior).forEach(function (k) { if (anterior[k] && !estado.categorias[k]) apagarCookies(k); });
      if (cfg.recarregarAoRevogar) window.location.reload();
    }
  }

  function salvar(categorias) {
    var anterior = estado ? estado.categorias : null;
    categorias.necessarios = true;
    estado = { versao: cfg.versao, data: new Date().toISOString(), categorias: categorias };
    gravar(estado);
    fecharBanner();
    fecharPainel();
    aplicar(anterior);
  }

  function todas(valor) {
    var c = {};
    cfg.categorias.forEach(function (cat) { c[cat.id] = cat.obrigatoria ? true : valor; });
    return c;
  }

  // ------------------------------------------------------------- interface
  function linkPolitica() {
    return el('a', { href: cfg.urlPolitica, texto: cfg.textos.linkPolitica });
  }

  function botoesPrincipais(dentroDoPainel) {
    var rejeitar = el('button', { type: 'button', classe: 'bc-botao', texto: cfg.textos.rejeitar });
    var aceitar = el('button', { type: 'button', classe: 'bc-botao', texto: cfg.textos.aceitarTodos });
    rejeitar.addEventListener('click', function () { salvar(todas(false)); });
    aceitar.addEventListener('click', function () { salvar(todas(true)); });
    var itens = [rejeitar];
    if (!dentroDoPainel) {
      var pref = el('button', { type: 'button', classe: 'bc-botao bc-botao-secundario', texto: cfg.textos.preferencias });
      pref.addEventListener('click', abrirPainel);
      itens.unshift(pref);
    }
    itens.push(aceitar);
    return el('div', { classe: 'bc-acoes' }, itens);
  }

  function mostrarBanner() {
    if (banner) return;
    var titulo = el('h2', { id: 'bc-titulo-banner', classe: 'bc-titulo', texto: cfg.textos.titulo });
    var p = el('p', { id: 'bc-descricao-banner', classe: 'bc-descricao' });
    p.appendChild(document.createTextNode(cfg.textos.descricao + ' '));
    p.appendChild(linkPolitica());
    p.appendChild(document.createTextNode('.'));
    banner = el('section', {
      classe: 'bc-banner', role: 'region', 'aria-labelledby': 'bc-titulo-banner',
      'aria-describedby': 'bc-descricao-banner'
    }, [el('div', { classe: 'bc-conteudo' }, [titulo, p]), botoesPrincipais(false)]);
    document.body.appendChild(banner);
  }

  function fecharBanner() {
    if (banner && banner.parentNode) banner.parentNode.removeChild(banner);
    banner = null;
  }

  function abrirPainel() {
    if (painel) return;
    focoAnterior = document.activeElement;
    var atuais = estado ? estado.categorias : {};
    var lista = el('div', { classe: 'bc-categorias' });
    cfg.categorias.forEach(function (cat) {
      var id = 'bc-cat-' + cat.id;
      var input = el('input', { type: 'checkbox', id: id, name: cat.id, 'aria-describedby': id + '-desc' });
      input.checked = !!(cat.obrigatoria || atuais[cat.id]);
      if (cat.obrigatoria) { input.disabled = true; input.checked = true; }
      var rotulo = el('label', { for: id, classe: 'bc-cat-nome' }, [input, document.createTextNode(' ' + cat.nome)]);
      var cabecalho = el('div', { classe: 'bc-cat-cabecalho' }, [rotulo]);
      if (cat.obrigatoria) cabecalho.appendChild(el('span', { classe: 'bc-sempre', texto: cfg.textos.sempreAtivo }));
      lista.appendChild(el('div', { classe: 'bc-categoria' }, [
        cabecalho, el('p', { id: id + '-desc', classe: 'bc-cat-desc', texto: cat.descricao })
      ]));
    });
    var salvarBtn = el('button', { type: 'button', classe: 'bc-botao', texto: cfg.textos.salvar });
    salvarBtn.addEventListener('click', function () {
      var cats = {};
      cfg.categorias.forEach(function (cat) {
        cats[cat.id] = cat.obrigatoria || document.getElementById('bc-cat-' + cat.id).checked;
      });
      salvar(cats);
    });
    var fechar = el('button', { type: 'button', classe: 'bc-fechar', 'aria-label': cfg.textos.fechar, texto: '×' });
    fechar.addEventListener('click', fecharPainel);
    var descricao = el('p', { id: 'bc-desc-painel', classe: 'bc-descricao' });
    descricao.appendChild(document.createTextNode(cfg.textos.descricao + ' '));
    descricao.appendChild(linkPolitica());
    descricao.appendChild(document.createTextNode('.'));
    var caixa = el('div', {
      classe: 'bc-painel', role: 'dialog', 'aria-modal': 'true',
      'aria-labelledby': 'bc-titulo-painel', 'aria-describedby': 'bc-desc-painel'
    }, [
      fechar,
      el('h2', { id: 'bc-titulo-painel', classe: 'bc-titulo', texto: cfg.textos.tituloPreferencias, tabindex: '-1' }),
      descricao, lista,
      el('div', { classe: 'bc-acoes' }, [botoesPrincipais(true), salvarBtn])
    ]);
    painel = el('div', { classe: 'bc-fundo' }, [caixa]);
    painel.addEventListener('keydown', prenderFoco);
    painel.addEventListener('click', function (e) { if (e.target === painel) fecharPainel(); });
    document.body.appendChild(painel);
    document.getElementById('bc-titulo-painel').focus();
  }

  function fecharPainel() {
    if (!painel) return;
    painel.parentNode.removeChild(painel);
    painel = null;
    if (focoAnterior && typeof focoAnterior.focus === 'function' && document.contains(focoAnterior)) {
      focoAnterior.focus();
    } else if (banner) {
      var b = banner.querySelector('button');
      if (b) b.focus();
    }
  }

  function prenderFoco(e) {
    if (e.key === 'Escape') { e.preventDefault(); fecharPainel(); return; }
    if (e.key !== 'Tab') return;
    var focaveis = painel.querySelectorAll('button:not([disabled]), input:not([disabled]), a[href]');
    if (!focaveis.length) return;
    var primeiro = focaveis[0];
    var ultimo = focaveis[focaveis.length - 1];
    if (e.shiftKey && (document.activeElement === primeiro || !painel.contains(document.activeElement))) {
      e.preventDefault(); ultimo.focus();
    } else if (!e.shiftKey && document.activeElement === ultimo) {
      e.preventDefault(); primeiro.focus();
    }
  }

  // ------------------------------------------------------------------ API
  window.blindagemConsent = {
    tem: permitido,
    obter: function () { return estado ? copiar(estado.categorias) : null; },
    definir: function (categorias) { salvar(mesclar(todas(false), categorias || {})); },
    abrirPreferencias: abrirPainel,
    revogar: function () {
      var anterior = estado ? estado.categorias : null;
      try { window.localStorage.removeItem(cfg.chave); } catch (e) { /* ignore */ }
      document.cookie = cfg.chave + '=; max-age=0; path=/';
      estado = null;
      if (anterior) Object.keys(anterior).forEach(apagarCookies);
      if (cfg.recarregarAoRevogar) window.location.reload(); else mostrarBanner();
    }
  };

  // --------------------------------------------------------------- início
  function iniciar() {
    estado = ler();
    document.addEventListener('click', function (e) {
      var alvo = e.target && e.target.closest ? e.target.closest('[data-abrir-preferencias-cookies]') : null;
      if (alvo) { e.preventDefault(); abrirPainel(); }
    });
    if (estado) {
      aplicar(null);
    } else {
      tratarIframes();
      mostrarBanner();
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
