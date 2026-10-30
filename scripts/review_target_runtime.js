/* Context-local target resolution. Visibility alone never proves a business condition. */
(function (host) {
  'use strict';
  function visible(node) {
    if (!node || !node.isConnected || !node.getClientRects().length) return false;
    for (let e = node; e && e.nodeType === 1; e = e.parentElement) {
      const s = e.ownerDocument.defaultView.getComputedStyle(e);
      if (e.hidden || s.display === 'none' || ['hidden','collapse'].includes(s.visibility) || s.opacity === '0') return false;
      if (e.tagName === 'DETAILS' && !e.open && !e.querySelector(':scope > summary')?.contains(node)) return false;
    }
    return true;
  }
  function resolve({root, selector, required = true, applicability = null}) {
    if (!selector) return required ? {status:'invalid_selector', error:'需要定位的说明缺少选择器', count:0} : {status:'system', system:true, count:0};
    if (!root || !visible(root)) return {status:'missing_context', error:'当前业务上下文不存在或不可见', count:0};
    let all;
    try { all = [...new Set([...(root.matches(selector) ? [root] : []), ...root.querySelectorAll(selector)])]; }
    catch { return {status:'invalid_selector', error:'定位选择器无效', count:0}; }
    const xs = all.filter(visible);
    // The caller supplies an observed product condition, never a prose fallback.
    const proven = applicability && typeof applicability.applies === 'boolean' &&
      applicability.reason && Array.isArray(applicability.source_refs) && applicability.source_refs.length &&
      applicability.observed && Object.keys(applicability.observed).length;
    if (xs.length > 1) return {status:'ambiguous', error:'目标不唯一', count:xs.length};
    if (proven && !applicability.applies) {
      if (xs.length) return {status:'condition_conflict', error:'适用条件不成立，但目标仍显示', count:xs.length, applicability};
      return {status:'not_applicable', count:0, applicability};
    }
    if (xs.length === 1) return {status:'visible', el:xs[0], count:1, applicability};
    if (proven && applicability.applies) return {status:'missing', error:'当前条件要求显示，目标却未出现', count:0, applicability};
    if (applicability || all.length) return {status:'unverified', error:'目标未显示；适用条件尚无可核验的观察', count:0, applicability};
    return {status:'missing', error:'当前上下文找不到定位目标，请检查选择器或补充真实适用条件', count:0};
  }
  const api = {resolve, visible};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else host.ADSReviewTargets = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
