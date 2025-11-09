import React, {useEffect, useMemo, useState} from "react";

const PAGE_SIZE = 8;

function App() {
    const [cards, setCards] = useState([]);
    const [loading, setLoading] = useState(false);

    // Filters
    const [gemRate, setGemRate] = useState(0.4);
    const [netGain, setNetGain] = useState(60);
    const [totalCost, setTotalCost] = useState(250);
    const [lucrativeFactor, setLucrativeFactor] = useState(0.6);
    const [psa10Volume, setPsa10Volume] = useState(20);
    const [targetDate, setTargetDate] = useState("2014-02-01");
    const [search, setSearch] = useState("");

    // UI toggles
    const [showLinks, setShowLinks] = useState(true);
    const [showDetails, setShowDetails] = useState(true);
    const [useCAD, setUseCAD] = useState(true);

    // Pagination
    const [page, setPage] = useState(0);

    const params = new URLSearchParams({
        gem_rate: gemRate,
        net_gain: netGain,
        total_cost: totalCost,
        lucrative_factor: lucrativeFactor,
        psa10_volume: psa10Volume,
        target_date: targetDate,
        search,
    }).toString();

    const fetchCards = async () => {
        setLoading(true);
        try {
            const res = await fetch(`/api/cards/filter?${params}`);
            const data = await res.json();
            setCards(data || []);
            setPage(0); // reset page after new fetch
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCards();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []); // initial load

    const totalPages = useMemo(() => Math.ceil((cards?.length || 0) / PAGE_SIZE), [cards]);
    const pageCards = useMemo(() => {
        const start = page * PAGE_SIZE;
        return cards.slice(start, start + PAGE_SIZE);
    }, [cards, page]);

    return (<div style={{padding: 16}}>
        <h2>Card Viewer (React + Flask)</h2>

        <div style={{display: "flex", gap: 16, alignItems: "flex-start", padding: 16, flexWrap: "wrap"}}>
            {/* Search Filter */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <label htmlFor="search" style={{fontWeight: "bold", marginBottom: 4}}>Search</label>
                <input
                    id="search"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Enter keyword..."
                    style={{
                        padding: 8, fontSize: 14, border: "1px solid #ccc", borderRadius: 4, width: 120, // Adjust input width for consistency
                    }}
                />
            </div>

            {/* Gem Rate */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <label htmlFor="gemRate" style={{fontWeight: "bold", marginBottom: 4}}>Gem Rate</label>
                <input
                    id="gemRate"
                    type="number"
                    step="0.01"
                    value={gemRate}
                    onChange={(e) => setGemRate(parseFloat(e.target.value || 0))}
                    style={{
                        padding: 8, fontSize: 14, border: "1px solid #ccc", borderRadius: 4, width: 120,
                    }}
                />
            </div>

            {/* Net Gain */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <label htmlFor="netGain" style={{fontWeight: "bold", marginBottom: 4}}>Net Gain</label>
                <input
                    id="netGain"
                    type="number"
                    step="0.01"
                    value={netGain}
                    onChange={(e) => setNetGain(parseFloat(e.target.value || 0))}
                    style={{
                        padding: 8, fontSize: 14, border: "1px solid #ccc", borderRadius: 4, width: 120,
                    }}
                />
            </div>

            {/* Total Cost */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <label htmlFor="totalCost" style={{fontWeight: "bold", marginBottom: 4}}>Total Cost</label>
                <input
                    id="totalCost"
                    type="number"
                    step="0.01"
                    value={totalCost}
                    onChange={(e) => setTotalCost(parseFloat(e.target.value || 0))}
                    style={{
                        padding: 8, fontSize: 14, border: "1px solid #ccc", borderRadius: 4, width: 120,
                    }}
                />
            </div>

            {/* Lucrative Factor */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <label htmlFor="lucrativeFactor" style={{fontWeight: "bold", marginBottom: 4}}>Lucrative
                    Factor</label>
                <input
                    id="lucrativeFactor"
                    type="number"
                    step="0.01"
                    value={lucrativeFactor}
                    onChange={(e) => setLucrativeFactor(parseFloat(e.target.value || 0))}
                    style={{
                        padding: 8, fontSize: 14, border: "1px solid #ccc", borderRadius: 4, width: 120,
                    }}
                />
            </div>

            {/* PSA Volume */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <label htmlFor="psa10Volume" style={{fontWeight: "bold", marginBottom: 4}}>PSA 10 Volume</label>
                <input
                    id="psa10Volume"
                    type="number"
                    value={psa10Volume}
                    onChange={(e) => setPsa10Volume(parseInt(e.target.value || 0, 10))}
                    style={{
                        padding: 8, fontSize: 14, border: "1px solid #ccc", borderRadius: 4, width: 120,
                    }}
                />
            </div>

            {/* Target Date */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <label htmlFor="targetDate" style={{fontWeight: "bold", marginBottom: 4}}>Target Date</label>
                <input
                    id="targetDate"
                    type="date"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                    style={{
                        padding: 8, fontSize: 14, border: "1px solid #ccc", borderRadius: 4, width: 120,
                    }}
                />
            </div>

            {/* Filter Button */}
            <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                <button
                    onClick={fetchCards}
                    style={{
                        marginTop: 22, // Align button to input fields
                        padding: "10px 16px",
                        backgroundColor: "#007BFF",
                        color: "white",
                        border: "none",
                        borderRadius: 4,
                        fontSize: 14,
                        cursor: "pointer",
                        minWidth: 120, // Uniform width
                    }}
                >
                    Apply Filters
                </button>
            </div>
        </div>

        <div style={{display: "flex", gap: 8, marginBottom: 12}}>
            <button onClick={() => setUseCAD((v) => !v)}>Toggle USD/CAD</button>
            <button onClick={() => setShowLinks((v) => !v)}>Toggle Links</button>
            <button onClick={() => setShowDetails((v) => !v)}>Toggle Details</button>
        </div>

        <div style={{marginBottom: 12}}>
            <button disabled={page === 0} onClick={() => setPage((p) => Math.max(p - 1, 0))}>
                {"<< Prev"}
            </button>
            <span style={{margin: "0 8px"}}>
          Page {page + 1} / {Math.max(totalPages, 1)}
        </span>
            <button disabled={page >= totalPages - 1}
                    onClick={() => setPage((p) => Math.min(p + 1, totalPages - 1))}>
                {"Next >>"}
            </button>
        </div>

        {loading ? (<div>Loading...</div>) : (
            <div style={{display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12}}>
                {pageCards.map((card, idx) => (<Card
                    key={idx}
                    card={card}
                    showDetails={showDetails}
                    showLinks={showLinks}
                    useCAD={useCAD}
                />))}
            </div>)}
    </div>);
}

// Components declared below App()
const CardImage = ({localImage, imgUrl, name}) => (
    <div style={{height: 170, display: "flex", alignItems: "center", justifyContent: "center", background: "#f3f3f3"}}>
        <img
            alt={name || "card"}
            src={`http://127.0.0.1:5000/static/assets/images/${localImage}`}
            style={{maxHeight: 160, objectFit: "contain"}}
        />
    </div>);

const CardDetails = ({card, showDetails, useCAD}) => {
    const conversionRate = useCAD ? 1.35 : 1;
    const currencyLabel = useCAD ? "CAD" : "USD";

    if (!showDetails) {
        const {averagePrice, salesDetails} = calculateSalesData(card, conversionRate, currencyLabel);

        return (<>
                <b>
                    {card.name.slice(0, 20)} {card.card_data?.num}
                    <br/>
                    {card.card_data?.set_name}
                </b>
                <br/>
                Average Sold: ${averagePrice.toFixed(2)} {currencyLabel}
                <br/>
                <pre style={{whiteSpace: "pre-wrap", fontSize: 12, margin: 0}}>
                  {salesDetails}
                </pre>
            </>);
    }

    return (<>
        <b>
            {card.name.slice(0, 20)} {card.card_data?.num}
            <br/>
            {card.card_data?.set_name}
        </b>
        <br/>
        Raw Price: ${parseFloat(card.raw_price * conversionRate).toFixed(2)} {currencyLabel}
        <br/>
        PSA 10 Price: ${parseFloat(card.psa_10_price * conversionRate).toFixed(2)} {currencyLabel}
        <br/>
        Gem Rate: {Math.round(card.gem_rate * 100)}%
        <br/>
        Expected Value: ${parseFloat(card.ev * conversionRate).toFixed(2)} {currencyLabel}
        <br/>
        Initial Cost: ${parseFloat(card.total_cost * conversionRate).toFixed(2)} {currencyLabel}
        <br/>
        Net Gain: ${parseFloat(card.net_gain * conversionRate).toFixed(2)} {currencyLabel}
        <br/>
        Lucrative Factor: {card.lucrative_factor.toFixed(2)}
        <br/>
        10 Pop: {card.psa_10_pop} | Other Pop: {card.non_psa_10_pop}
        <br/>
        Sales: {card.psa10_volume}(PSA10) {card.non_psa10_volume}(Other)
    </>);
};

const CardLinks = ({card, showLinks}) => {
    if (!showLinks) return null;

    const url = `https://www.pokedata.io/card/${(card.set_name || "").replaceAll(" ", "+")}/${(card.name || "")
        .replaceAll(" ", "+")}+${card.card_data?.num}`;

    return (<div style={{marginTop: 6}}>
        <a href={url} target="_blank" rel="noreferrer">Open in Browser</a>
    </div>);
};

const Card = ({card, showDetails, showLinks, useCAD}) => (<div style={{border: "1px solid #ddd", padding: 8}}>
    <CardImage
        localImage={card.local_image}
        imgUrl={card.card_data?.img_url}
        name={card.card_data?.name}
    />
    <div style={{marginTop: 8, fontSize: 14, whiteSpace: "pre-wrap"}}>
        <CardDetails card={card} showDetails={showDetails} useCAD={useCAD}/>
    </div>
    <CardLinks card={card} showLinks={showLinks}/>
</div>);

const calculateSalesData = (card, conversionRate, currencyLabel) => {
    let averagePrice = 0;
    let salesDetails = "";

    try {
        // Parse the sales and remove the highest and lowest sold_price.
        const sales = card.recent_raw_ebay_sales || [];
        const filteredSales = sales.sort((a, b) => a.sold_price - b.sold_price).slice(2, -1);

        // Sort the remaining sales by date_sold.
        const sortedSalesByDate = filteredSales.sort((a, b) => new Date(b.date_sold).getTime() - new Date(a.date_sold).getTime());

        // Calculate the average sold price.
        if (sortedSalesByDate.length > 0) {
            averagePrice = sortedSalesByDate.reduce((sum, sale) => sum + sale.sold_price, 0) / sortedSalesByDate.length;
        }

        // Format sales details with DD/MM/YYYY date format.
        salesDetails = sortedSalesByDate
            .map((sale) => {
                const saleDate = new Date(sale.date_sold);
                const formattedDate = `${String(saleDate.getDate()).padStart(2, '0')}/${String(saleDate.getMonth() + 1).padStart(2, '0')}/${saleDate.getFullYear()}`;
                return `${formattedDate}: $${(sale.sold_price * conversionRate).toFixed(2)} ${currencyLabel}`;
            })
            .join("\n");
    } catch (e) {
        salesDetails = "Date format error. Unable to parse some dates.";
        console.error("Error parsing sales data:", e);
    }

    return {
        averagePrice, salesDetails,
    };
};

export default App;