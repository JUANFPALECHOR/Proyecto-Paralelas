from datetime import datetime
from typing import Optional
import re


_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def to_date(value: str) -> Optional[str]:
    """Parse various date formats into 'YYYY-MM-DD' string.

    Accepts formats like '2023-05-20', '20/05/2023', '20 de mayo de 2023'.
    Returns None if parsing fails.
    """
    if not isinstance(value, str) or not value:
        return None

    value = value.strip().lower()

    # ISO
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # DD/MM/YYYY
    try:
        if re.match(r"^\d{2}/\d{2}/\d{4}$", value):
            dt = datetime.strptime(value, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # '20 de mayo de 2023'
    m = re.match(r"^(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})$", value)
    if m:
        try:
            day = int(m.group(1))
            month_name = m.group(2).replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            month = _MONTHS.get(month_name)
            year = int(m.group(3))
            if month:
                dt = datetime(year, month, day)
                return dt.strftime("%Y-%m-%d")
        except Exception:
            pass

    return None
