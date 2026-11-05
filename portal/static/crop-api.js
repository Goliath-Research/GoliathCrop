(function () {
  const DEMO = "../static/demo-fixtures.json";

  function sessionToken() {
    return window.GOLIATH_SESSION && window.GOLIATH_SESSION.token;
  }

  function gatewayBase() {
    return (window.GOLIATH_SESSION && window.GOLIATH_SESSION.gatewayBase) || "";
  }

  async function runSemanticRequest(requestCode, params) {
    const base = gatewayBase();
    const token = sessionToken();
    if (!base || !token) {
      const demo = await fetch(DEMO).then((r) => r.json());
      return demo[requestCode] || [];
    }
    const response = await fetch(`${base}/v1/semantic/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ request_code: requestCode, params }),
    });
    if (!response.ok) {
      throw new Error(`semantic ${requestCode} failed (${response.status})`);
    }
    const body = await response.json();
    return body.rows || body.data || [];
  }

  async function runAction(actionName, input) {
    const base = gatewayBase();
    const token = sessionToken();
    if (!base || !token) {
      return { ok: true, demo: true, input };
    }
    const response = await fetch(`${base}/v1/actions/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ action_name: actionName, input }),
    });
    if (!response.ok) {
      throw new Error(`action ${actionName} failed (${response.status})`);
    }
    return response.json();
  }

  function setStatus(el, message, isError) {
    if (!el) return;
    el.textContent = message;
    el.classList.toggle("error", Boolean(isError));
  }

  function queryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  window.CropPortal = {
    runSemanticRequest,
    runAction,
    setStatus,
    queryParam,
  };
})();
