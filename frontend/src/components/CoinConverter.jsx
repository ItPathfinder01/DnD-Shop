import { useState } from "react";

const COINS = [
  { key: "platinum", label: "Платина (пп)", rate: 1000 },
  { key: "gold",     label: "Золото (зм)",  rate: 100 },
  { key: "electrum", label: "Электрум (эм)", rate: 50 },
  { key: "silver",   label: "Серебро (см)",  rate: 10 },
  { key: "copper",   label: "Медь (мм)",     rate: 1 },
];

export default function CoinConverter({ onExchange }) {
  const [from, setFrom] = useState("gold");
  const [to, setTo] = useState("copper");
  const [amount, setAmount] = useState("");
  const [result, setResult] = useState(null);
  const [exchangeMsg, setExchangeMsg] = useState(null);

  const convert = () => {
    const n = parseFloat(amount);
    if (isNaN(n) || n < 0) { setResult("Введите корректное количество"); return; }
    const fromRate = COINS.find((c) => c.key === from).rate;
    const toRate = COINS.find((c) => c.key === to).rate;
    const valueInCopper = n * fromRate;
    const converted = valueInCopper / toRate;
    const toLabel = COINS.find((c) => c.key === to).label;
    setResult(`${n} → ${Number.isInteger(converted) ? converted : converted.toFixed(4)} ${toLabel}`);
  };

  const exchange = async () => {
    const n = parseInt(amount);
    if (isNaN(n) || n <= 0) { setExchangeMsg("Введите корректное количество"); return; }
    try {
      await onExchange(from, to, n);
      setExchangeMsg("Обмен выполнен");
      setAmount("");
      setResult(null);
    } catch (err) {
      setExchangeMsg(err.response?.data?.detail || "Ошибка обмена");
    }
  };

  return (
    <div className="converter">
      <h4>Конвертер монет</h4>
      <label>Из:</label>
      <select value={from} onChange={(e) => { setFrom(e.target.value); setExchangeMsg(null); }}>
        {COINS.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
      </select>
      <input
        type="number" min={0} placeholder="Количество"
        value={amount} onChange={(e) => { setAmount(e.target.value); setExchangeMsg(null); }}
      />
      <label>В:</label>
      <select value={to} onChange={(e) => { setTo(e.target.value); setExchangeMsg(null); }}>
        {COINS.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
      </select>
      <button onClick={convert}>Конвертировать</button>
      {result && <p className="result">{result}</p>}
      {onExchange && (
        <>
          <button onClick={exchange}>Обмен</button>
          {exchangeMsg && <p className="result">{exchangeMsg}</p>}
        </>
      )}
    </div>
  );
}
