"""
Complete Stock Universe - US Stocks, Canadian Stocks, and ETFs
Includes major indices and popular ETFs from both markets
"""

# US Major Stocks - S&P 500, NASDAQ, Dow Jones
US_STOCKS = {
    # Mega Cap Tech
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "GOOG", "META", "TSLA", "BRK-B",
    "UNH", "LLY", "JPM", "V", "AVGO", "XOM", "MA", "HD", "PG", "COST",

    # Tech Sector
    "AMD", "INTC", "CSCO", "ORCL", "IBM", "TXN", "QCOM", "ADBE", "CRM", "INTU",
    "AMAT", "MU", "LRCX", "NOW", "UBER", "SNOW", "PLTR", "ZM", "ROKU", "SQ",
    "PANW", "NET", "DDOG", "MDB", "CRWD", "OKTA", "TWLO", "FSLY", "ESTC", "ASAN",
    "SHOP", "UPST", "SOFI", "HOOD", "COIN", "RBLX", "U", "WIX", "DOCU", "NYSE",

    # Financials
    "BAC", "GS", "MS", "WFC", "C", "AXP", "BLK", "CME", "SPGI", "ICE",
    "USB", "PNC", "COF", "SCHW", "BK", "TROW", "APO", "BX", "KKR", "CG",

    # Healthcare
    "PFE", "AZN", "BMY", "ABBV", "DHR", "GILD", "GSK", "AMGN", "CVS", "CI",
    "TMO", "ABT", "MRK", "JNJ", "UNH", "ELV", "HUM", "CNC", "MOH", "REGN",
    "VRTX", "BIIB", "ALNY", "MRNA", "BNTX", "IONQ", "DNA", "TXG", "CRSP", "EDIT",

    # Energy & Materials
    "XOM", "CVX", "COP", "EOG", "SLB", "OXY", "MPC", "VLO", "PSX", "KMI",
    "WMB", "EPD", "ET", "MPLX", "PXD", "DVN", "FANG", "MRO", "OKE", "TRGP",

    # Consumer
    "AMZN", "WMT", "HD", "COST", "TGT", "LOW", "CVS", "WBA", "NKE", "MCD",
    "SBUX", "YUM", "DPZ", "CMG", "DRI", "MAR", "HLT", "ABNB", "BKNG", "EXPE",
    "TJX", "ROST", "BURL", "DG", "DLTR", "FIVE", "ULTA", "WSM", "RH", "ETSY",

    # Communications
    "NFLX", "DIS", "CMCSA", "VZ", "T", "TMUS", "CHTR", "LUMN", "TTWO", "EA",
    "SPOT", "PINS", "SNAP", "MTCH", "IAC", "NYT", "NLSN", "CCO", "OUT", "LAMR",

    # Industrial
    "CAT", "HON", "BA", "UNP", "UPS", "FDX", "GE", "RTX", "LMT", "NOC",
    "MMM", "ITW", "EMR", "ETN", "CSX", "NSC", "WM", "RSG", "CWST", "GFL",
}

# Canadian Stocks - TSX
CANADIAN_STOCKS = {
    # Major Banks
    "RY.TO", "TD.TO", "BNS.TO", "BMO.TO", "CM.TO", "NA.TO",

    # Energy
    "ENB.TO", "TRP.TO", "CNQ.TO", "SU.TO", "IMO.TO", "CVE.TO", "ARX.TO",
    "CPG.TO", "WCP.TO", "OVV.TO", "TOU.TO", "PNE.TO", "BIR.TO",

    # Mining & Materials
    "FNV.TO", "WPM.TO", "AEM.TO", "ABX.TO", "NTR.TO", "TECK.B.TO", "FM.TO",
    "CS.TO", "OR.TO", "EQT.TO", "SSRM.TO", "PAAS.TO", "AGI.TO", "YRI.TO",

    # Technology
    "SHOP.TO", "CSU.TO", "OTEX.TO", "ENGH.TO", "DSG.TO", "LSPD.TO", "DCBO.TO",
    "REAL.TO", "NVEI.TO", "PAY.TO", "FOOD.TO", "ET.TO", "VHI.TO", "ADCO.TO",

    # Utilities & Infrastructure
    "CP.TO", "CNR.TO", "WCN.TO", "ATD.TO", "BN.TO", "POW.TO", "IFC.TO",
    "MRU.TO", "DOL.TO", "WN.TO", "L.TO", "SXC.TO", "EFN.TO", "CIX.TO",

    # REITs
    "REI.UN.TO", "H.RT.UN.TO", "CAR.UN.TO", "AP.UN.TO", "SOT.UN.TO",
    "BEP.UN.TO", "BIP.UN.TO", "BPY.UN.TO", "INE.TO", "NPI.TO",

    # Telecom
    "T.TO", "RCI.B.TO", "BCE.TO", "QBR.B.TO", "CCA.TO", "SJR.B.TO",

    # Cannabis
    "WEED.TO", "ACB.TO", "TLRY.TO", "CRON.TO", "HEXO.TO", "VFF.TO",

    # Other
    "SU.TO", "CVE.TO", "IMO.TO", "ARX.TO", "WCP.TO", "CPG.TO", "TOU.TO",
}

# US ETFs - Major and Popular
US_ETFS = {
    # Broad Market
    "SPY", "VOO", "VTI", "VTV", "VUG", "VO", "VB", "VXF", "VOE", "VBR",
    "IVV", "IWF", "IWD", "IWM", "IWN", "IWO", "ITOT", "IWV", "IYY", "IUSG",

    # Sector ETFs
    "XLK", "XLF", "XLE", "XLI", "XLP", "XLU", "XLV", "XLY", "XLB", "XLRE",
    "VGT", "VFH", "VDE", "VIS", "VDC", "VPU", "VHT", "VCR", "VAW", "VNQ",
    "IYT", "IYF", "IYE", "IYW", "IYZ", "IYH", "IYK", "IYM", "IDU", "IYG",

    # Bond ETFs
    "TLT", "IEF", "SHY", "LQD", "HYG", "AGG", "BND", "VCIT", "VCLT", "VGIT",
    "TIP", "SCHP", "PFF", "SPAB", "SPIP", "SPTL", "SPTI", "GOVT",

    # International
    "VXUS", "VT", "VEU", "VWO", "VGK", "VPL", "VSS", "VEA", "VIGI", "VYMI",
    "EEM", "EFA", "IEFA", "IEMG", "ACWI", "VTI", "IXUS", "SCHF", "SCHE",

    # Thematic/Technology
    "ARKK", "ARKQ", "ARKW", "ARKG", "ARKF", "ARKX",
    "SMH", "SOXX", "SOXL", "SOXS", "XSD", "PSI", "FTXL", "QTEC",
    "CIBR", "HACK", "CLOU", "SKYY", "IGV", "XSW", "BUG", "DRIV", "IDRV",
    "FINX", "IEIH", "KRBN", "LIT", "PHO", "PBW", "QCLN", "ICLN", "FAN",

    # Crypto & Bitcoin
    "BITO", "BITI", "ARKB", "IBIT", "FBTC", "BTCO", "BITB", "HODL", "BRRR",
    "ETHE", "ETF", "MSTR", "COIN", "RIOT", "MARA", "CORZ", "CLSK", "BTBT",

    # Commodities
    "GLD", "IAU", "SLV", "SLVO", "USO", "UNG", "DBC", "GSG", "PDBC", "BCI",
    "GLDM", "BAR", "SGOL", "AAAU", "OUNZ", "SLVO", "SLV", "SIVR",

    # Leveraged/Inverse
    "TQQQ", "SQQQ", "UPRO", "SPXU", "UDOW", "SDOW", "URTY", "SRTY",
    "TNA", "TZA", "FAS", "FAZ", "LABU", "LABD", "SOXL", "SOXS",

    # Dividend
    "VYM", "SCHD", "DGRO", "HDV", "SPHD", "NOBL", "SDY", "DVY", "FDL", "PEY",
}

# Canadian ETFs
CANADIAN_ETFS = {
    # Broad Market
    "XIU.TO", "XIC.TO", "VCN.TO", "ZCN.TO", "HXT.TO", "ZUE.TO", "XSP.TO",
    "VUS.TO", "XUU.TO", "VFV.TO", "XUS.TO", "ZSP.TO", "HSH.TO",

    # Canadian Dividend
    "XDV.TO", "ZDV.TO", "VDY.TO", "CDZ.TO", "HXH.TO", "XEI.TO", "ZMI.TO",

    # Canadian Bonds
    "XBB.TO", "ZAG.TO", "VAB.TO", "XCB.TO", "ZDB.TO", "BXF.TO", "XSB.TO",
    "XGB.TO", "QBB.TO", "ZIC.TO", "VSB.TO", "CLF.TO", "CBO.TO",

    # Sector
    "XEG.TO", "ZJN.TO", "HXU.TO", "HXD.TO", "XEN.TO", "ZEO.TO", "XFN.TO",
    "ZEB.TO", "XRE.TO", "VRE.TO", "ZRE.TO", "XIT.TO", "XGD.TO", "CGL.TO",
    "HGU.TO", "HGD.TO", "XBM.TO", "ZEM.TO", "XMA.TO", "ZUM.TO",

    # International
    "XEF.TO", "VI.TO", "ZEA.TO", "XEC.TO", "VEE.TO", "ZEM.TO", "XEM.TO",
    "VE.TO", "XMU.TO", "HZU.TO", "HZD.TO",

    # Preferred Shares
    "CPD.TO", "ZPR.TO", "XPF.TO", "HPR.TO", "PDC.TO", "ZHP.TO",

    # Monthly Income
    "ZWB.TO", "FIE.TO", "ZWC.TO", "ZWH.TO", "HEWB.TO", "ZWK.TO",

    # Gold
    "GLD", "IAU", "MNT.TO", "CGL.CA", "XGD.TO", "ZSP.TO",

    # ESG/Sustainable
    "ESG.TO", "XESG.TO", "HXS.TO", "VGG.TO", "VXC.TO", "EAGG.TO",

    # Covered Call
    "ZWB.TO", "ZWU.TO", "ZWC.TO", "ZWH.TO", "HHL.TO", "TLF.TO",
}

# Combine all into master set
def get_full_universe(market: str = 'all') -> set:
    """
    Get full stock/ETF universe

    Args:
        market: 'us', 'ca', 'all', or 'etfs'

    Returns:
        Set of ticker symbols
    """
    if market == 'us':
        return US_STOCKS
    elif market == 'ca':
        return CANADIAN_STOCKS | CANADIAN_ETFS
    elif market == 'etfs':
        return US_ETFS | CANADIAN_ETFS
    elif market == 'all':
        return US_STOCKS | CANADIAN_STOCKS | US_ETFS | CANADIAN_ETFS
    else:
        return US_STOCKS | CANADIAN_STOCKS

# Default universe for scanner
DEFAULT_STOCKS = get_full_universe('all')

# Get count
if __name__ == "__main__":
    print(f"US Stocks: {len(US_STOCKS)}")
    print(f"Canadian Stocks: {len(CANADIAN_STOCKS)}")
    print(f"US ETFs: {len(US_ETFS)}")
    print(f"Canadian ETFs: {len(CANADIAN_ETFS)}")
    print(f"Total Universe: {len(DEFAULT_STOCKS)}")
