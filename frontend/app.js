"use strict";
/* Client for the unchanged V7 FastAPI endpoints. Fictional demonstration only. */
(() => {
  const $ = (id) => document.getElementById(id);
  const els = {
    status: $("api-status"), feeder: $("feeder"), study: $("study-code"),
    coordinates: $("selected-coordinates"), calculate: $("calculate"),
    save: $("save"), restore: $("restore"), list: $("list"),
    clear: $("clear"), studyList: $("study-list"), message: $("messages"),
    mf: $("metric-feeder"), mp: $("metric-phase"), md: $("metric-distance"), ms: $("metric-state")
  };
  const format = new ol.format.GeoJSON();
  const networkSource = new ol.source.Vector();
  const resultSource = new ol.source.Vector();
  const networkLayer = new ol.layer.Vector({
    source: networkSource,
    style: new ol.style.Style({
      stroke: new ol.style.Stroke({color: "#0789b1", width: 3.5})
    })
  });
  const resultLayer = new ol.layer.Vector({
    source: resultSource,
    style: (feature) => {
      const kind = feature.get("kind");
      const color = kind === "selected" ? "#e33757" : kind === "connection" ? "#ef8b19" : "#d22a80";
      return new ol.style.Style({
        stroke: new ol.style.Stroke({color, width: 4, lineDash: kind === "line" ? [9, 7] : undefined}),
        image: new ol.style.Circle({
          radius: kind === "selected" ? 8 : 7,
          fill: new ol.style.Fill({color}),
          stroke: new ol.style.Stroke({color: "#ffffff", width: 2})
        })
      });
    }
  });
  const map = new ol.Map({
    target: "map",
    layers: [
      new ol.layer.Tile({
        source: new ol.source.XYZ({
          url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
          attributions: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>'
        })
      }),
      networkLayer,
      resultLayer
    ],
    view: new ol.View({
      center: ol.proj.fromLonLat([-47.06, -22.91]),
      zoom: 12
    })
  });

  let selected = null;
  let calculation = null;
  let sequence = 0;

  function notify(message, error = false) {
    els.message.textContent = message;
    els.message.classList.toggle("error", error);
  }
  function updateButtons() {
    const feederReady = Boolean(els.feeder.value);
    const codeReady = Boolean(els.study.value.trim());
    els.calculate.disabled = !feederReady || !selected;
    els.save.disabled = !feederReady || !codeReady || !calculation;
    els.restore.disabled = !feederReady || !codeReady;
    els.list.disabled = !feederReady;
  }
  function resetResult() {
    selected = null;
    calculation = null;
    resultSource.clear();
    els.coordinates.textContent = "No point selected";
    els.mf.textContent = els.mp.textContent = els.md.textContent = "—";
    els.ms.textContent = "Waiting";
    updateButtons();
  }
  function endpoint(suffix) {
    return "/alimentadores/" + encodeURIComponent(els.feeder.value) + suffix;
  }
  async function api(url, options = {}) {
    const response = await fetch(url, options);
    const type = response.headers.get("content-type") || "";
    if (!type.includes("json")) throw new Error("Unexpected response from server (HTTP " + response.status + ")");
    const body = await response.json();
    if (!response.ok) throw new Error("HTTP " + response.status + ": " + (body.detail || "Request failed"));
    return body;
  }
  function post(point) {
    return {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({longitude: point[0], latitude: point[1]})
    };
  }
  function addGeometry(geometry, kind) {
    if (!geometry) return;
    const feature = format.readFeature({
      type: "Feature", geometry, properties: {}
    }, {dataProjection: "EPSG:4326", featureProjection: "EPSG:3857"});
    feature.set("kind", kind);
    resultSource.addFeature(feature);
  }
  function displayStudy(data, restored = false) {
    calculation = data;
    selected = data.selected_point?.coordinates || null;
    resultSource.clear();
    addGeometry(data.selected_point, "selected");
    addGeometry(data.connection_point, "connection");
    addGeometry(data.connection_line, "line");
    els.coordinates.textContent = selected ? selected.map(x => x.toFixed(6)).join(", ") : "—";
    els.mf.textContent = data.feeder || "—";
    els.mp.textContent = data.phase || "—";
    els.md.textContent = typeof data.length_km === "number"
      ? data.length_km.toFixed(3) + " km" : "—";
    els.ms.textContent = restored ? "Restored" : "Calculated";
    updateButtons();
    if (restored && resultSource.getFeatures().length) {
      map.getView().fit(resultSource.getExtent(), {
        padding: [80, 90, 80, 90], maxZoom: 16, duration: 350
      });
    }
  }
  function showError(error) {
    notify(error instanceof Error ? error.message : String(error), true);
  }

  async function loadFeeders() {
    try {
      await api("/health");
      els.status.textContent = "API online";
      els.status.classList.add("online");
      const data = await api("/alimentadores");
      els.feeder.replaceChildren(new Option("Choose a fictional feeder", ""));
      for (const f of data.alimentadores || []) {
        els.feeder.add(new Option(f.ctmt + " · " + f.segment_count + " segments", f.ctmt));
      }
      notify("API connected. Select a fictional feeder.");
    } catch (error) {
      els.status.textContent = "API offline";
      els.status.classList.add("offline");
      els.feeder.replaceChildren(new Option("Unable to load networks", ""));
      showError(error);
    }
  }

  els.feeder.addEventListener("change", async () => {
    const requestNumber = ++sequence;
    resetResult();
    networkSource.clear();
    els.studyList.replaceChildren();
    if (!els.feeder.value) return;
    const feeder = els.feeder.value;
    notify("Loading fictional network " + feeder + "...");
    try {
      const geojson = await api(endpoint("/ssdmt"));
      if (requestNumber !== sequence) return;
      const features = format.readFeatures(geojson, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3857"
      });
      networkSource.addFeatures(features);
      if (features.length) {
        map.getView().fit(networkSource.getExtent(), {
          padding: [50, 70, 50, 70], maxZoom: 15, duration: 300
        });
      }
      notify(feeder + ": " + features.length + " network segments loaded. Click the map to select a point.");
    } catch (error) {
      if (requestNumber === sequence) showError(error);
    }
    updateButtons();
  });
  map.on("singleclick", (event) => {
    if (!els.feeder.value) return;
    resetResult();
    selected = ol.proj.toLonLat(event.coordinate);
    addGeometry({type: "Point", coordinates: selected}, "selected");
    els.coordinates.textContent = selected.map(x => x.toFixed(6)).join(", ");
    notify("Point selected. Click Calculate connection.");
    updateButtons();
  });
  els.study.addEventListener("input", updateButtons);
  els.clear.addEventListener("click", () => {
    resetResult();
    notify("Selection cleared.");
  });
  els.calculate.addEventListener("click", async () => {
    if (!selected || !els.feeder.value) return;
    els.calculate.disabled = true;
    const feeder = els.feeder.value;
    try {
      const data = await api(endpoint("/connection"), post(selected));
      if (feeder !== els.feeder.value) return;
      displayStudy(data);
      notify("Connection calculated. The point and connection line are visible on the map.");
    } catch (error) { showError(error); }
    finally { updateButtons(); }
  });
  els.save.addEventListener("click", async () => {
    const code = els.study.value.trim();
    if (!code || !selected || !calculation) return;
    const feeder = els.feeder.value;
    els.save.disabled = true;
    try {
      const saved = await api(endpoint("/studies/" + encodeURIComponent(code)), post(selected));
      if (feeder !== els.feeder.value) return;
      displayStudy(saved);
      els.ms.textContent = "Saved";
      notify("Study " + code + " saved in SQLite (ID " + saved.id + ").");
    } catch (error) { showError(error); }
    finally { updateButtons(); }
  });
  els.restore.addEventListener("click", async () => {
    const code = els.study.value.trim();
    if (!code || !els.feeder.value) return;
    const feeder = els.feeder.value;
    try {
      const study = await api(endpoint("/studies/" + encodeURIComponent(code)));
      if (feeder !== els.feeder.value) return;
      displayStudy(study, true);
      // Restored studies must not be resaved under the same identifier.
      els.save.disabled = true;
      notify("Study " + code + " restored from SQLite, including the original point and connection line.");
    } catch (error) { showError(error); }
  });
  els.list.addEventListener("click", async () => {
    if (!els.feeder.value) return;
    try {
      const studies = await api(endpoint("/studies"));
      els.studyList.replaceChildren();
      if (!studies.length) { notify("No studies saved for this network."); return; }
      for (const study of studies) {
        const row = document.createElement("button");
        row.type = "button";
        row.className = "study-row";
        row.textContent = study.study_code + " · " + study.length_km.toFixed(3) + " km";
        row.addEventListener("click", () => {
          els.study.value = study.study_code;
          updateButtons();
          els.restore.click();
        });
        els.studyList.append(row);
      }
      notify(studies.length + " saved studies found. Click one to restore.");
    } catch (error) { showError(error); }
  });
  updateButtons();
  loadFeeders();
})();
