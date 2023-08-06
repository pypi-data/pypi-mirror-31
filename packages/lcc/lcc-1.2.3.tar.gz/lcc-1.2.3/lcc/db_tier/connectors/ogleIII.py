import requests
from astropy.coordinates.sky_coordinate import SkyCoord
from bs4 import BeautifulSoup
import re
import warnings

from lcc.db_tier.base_query import LightCurvesDb
from lcc.entities.exceptions import QueryInputError
from lcc.entities.star import Star
from lcc.utils.helpers import progressbar
import numpy as np


class OgleIII(LightCurvesDb):
    """
    Connector to OGLEIII

    Example:
    --------
    que1 = {"ra":72.798405,
            "dec": -69.00918, "delta": 5, "nearest": True}

    que2 = {"types" : ["DPV"], "target" : "lmc"}

    que3 = {"field": "LMC135.5", "starid" : 19670}

    client = StarsProvider().getProvider("OgleIII", [que1, que2, que3])
    stars = client.getStars()
    
    
    Possible keys for query:
                    ["ra", "dec", "delta", "nearest", "field", "starid", "types",
                    "mag_i_min", "mag_v_min", "mag_i_max", "mag_v_max",
                    "p1_min", "p1_max", "ogleii_id", "macho_id", "asas_id",
                    "gvcs_id", "remarks"]
    """

    ROOT = "http://ogledb.astrouw.edu.pl/~ogle/CVS/"
    SUFF = "query.php?first=1&qtype=catalog"

    MAX_TIMEOUT = 60
    DEFAULT_DELTA = 10

    LC_META = {"xlabel": "hjd",
               "xlabel_unit": "days",
               "ylabel": "magnitude",
               "ylabel_unit": "mag",
               "color": "I",
               "origin": "OgleIII"}

    COL_MAP = {"Field": "field",
               "StarID": "starid",
               "RA": "ra",
               "Decl": "dec",
               "V": "v_mag",
               "I": "i_mag",
               "Type": "type",
               "Subtype": "subtype",
               "P_1": "period",
               "A_1": "i_ampl",
               "ID_OGLE_II": "ogle_ii_id",
               "ID_MACHO": "macho_id",
               "ID_ASAS": "asas_id",
               "ID_GCVS": "gcvs_id",
               "ID_OTHER": "other_id",
               "Remarks": "remarks",
               "ID": "name"}

    MORE = ["i_mag", "type", "subtype", "remarks", "i_ampl", "period", "v_mag"]
    TYPES = ["Cep", "ACep", "LPV", "T2Cep", "RRLyr", "RCB", "DSCT", "DPV"]

    QUERY_OPTIONS = ["ra", "dec", "delta", "nearest", "field", "starid", "types",
                    "mag_i_min", "mag_v_min", "mag_i_max", "mag_v_max",
                    "p1_min", "p1_max", "ogleii_id", "macho_id", "asas_id",
                    "gvcs_id", "remarks"]

    def __init__(self, queries, multiproc=True):
        """
        Parameters
        ----------
        queries : list, dict, iterable
            Query is list of dictionaries of query parameters or single
            dictionary
            
        multiproc : bool, int
            If True task will be distributed into threads by using all cores. If it is number,
            just that number of cores are used
        """
        if isinstance(queries, dict):
            queries = [queries]
        self.queries = self._parseQueries(queries)
        self.multiproc = multiproc

    def getStar(self, query, load_lc=True):
        stars = self.postQuery(query, load_lc)
        if "ra" in query and "dec" in query and "delta" in query:
            stars = self.coneSearch(SkyCoord(float(query["ra"]), float(query["dec"]), unit="deg"),
                                    stars, float(query["delta"] / 3600.),
                                    nearest=query.get("nearest", False))
        return stars

    def postQuery(self, query, lc):
        PAGE_LEN = 1e10
        valmin_ra, valmax_ra, valmin_dec, valmax_dec = self._getRanges(query.get("ra"),
                                                                       query.get(
                                                                           "dec"),
                                                                       query.get("delta"))
        if valmax_ra and valmax_ra:
            valmax_ra = valmax_ra / 15.
            valmin_ra = valmin_ra / 15.

        params = {
            "db_target": query.get("target"),
            "dbtyp": "dia2",
            "sort": "field",
            "use_field": "field" in query,
            "val_field": query.get("field"),
            "disp_field": "on",
            "use_starid": "starid" in query,
            "val_starid": query.get("starid"),
            "disp_starid": "on",
            "disp_type": "on",
            "disp_subtype": "on",
            "disp_starcat": "off",
            "use_starcat": "off",
            "disp_ra": "on",
            "use_ra": valmin_ra != "",
            "valmin_ra": valmin_ra,
            "valmax_ra": valmax_ra,
            "disp_decl": "on",
            "use_decl": valmin_dec != "",
            "valmin_decl": valmin_dec,
            "valmax_decl": valmax_dec,
            "disp_imean": "on",
            "use_imean": "mag_i_min" in query,
            "valmin_i": query.get("mag_i_min"),
            "valmax_i": query.get("mag_i_max"),
            "valmin_v": query.get("mag_v_min"),
            "valmax_v": query.get("mag_v_max"),
            "disp_p1": "on",
            "valmin_p1": query.get("p1_min"),
            "valmax_p1": query.get("p1_max"),
            "disp_id_ogle_ii": "on",
            "val_id_ogle_ii": query.get("ogleii_id"),
            "disp_id_macho": "on",
            "val_id_macho": query.get("macho_id"),
            "disp_id_asas": "on",
            "val_id_asas": query.get("asas_id"),
            "disp_id_gcvs": "on",
            "val_id_gcvs": query.get("gvcs_id"),
            "disp_id_other": "on",
            "disp_remarsk": "on",
            "val_remarks": query.get("remarks"),
            "disp_vmean": "on",
            "disp_i": "on",
            "disp_v": "on",
            "sorting": "ASC",
            "pagelen": PAGE_LEN,
        }
        if "types" in query:
            star_types = {"use_type": "on"}
            if not hasattr(query["types"], "__iter__"):
                query["types"] = [query["types"]]
            for star_type in query["types"]:
                star_types["val_type"+star_type] = "on"

            params.update(star_types)

        # Delete unneeded parameters
        to_del = []
        for key, value in params.items():
            if not value or value == "off":
                to_del.append(key)
        # Url for query
        url = "%s/%s" % (self.ROOT, self.SUFF)
        [params.pop(x, None) for x in to_del]
        result = requests.post(url, params)
        return self._parseResult(result, lc=lc)

    def _parseQueries(self, queries):
        todel_queries = []
        new_queries = []
        for i, query in enumerate(queries):

            if "coo" in query and isinstance(query["coo"], SkyCoord):
                if not "delta" in query:
                    query["delta"] = self.DEFAULT_DELTA
                todel_queries.append(i)
                coo = query["coo"]
                new_queries.append(
                    {"ra": coo.ra.degree, "dec": coo.dec.degree,
                     "delta": query["delta"], "target": "all"})

            if "ra" in query and "dec" in query:
                if not "delta" in query:
                    query["delta"] = self.DEFAULT_DELTA

                if "target" not in query:
                    query["target"] = "all"

            elif "starid" in query:
                if "field" in query:
                    query["target"] = query["field"][:3].lower()
                elif "field_num" in query and "target" in query:
                    query["field"] = query[
                        "target"].upper() + "_SC" + str(query["field_num"])
                else:
                    raise QueryInputError("Unresolved target")

            if "types" in query and sum([1 for star_type in query["types"] if not star_type in self.TYPES]):
                raise QueryInputError("Invalid star type in the query.\nAvailable types: %s" % self.TYPES)

        return [item for i, item in enumerate(
            queries) if i not in todel_queries] + new_queries

    def _parseResult(self, result, lc=False):
        START_TABLE = "<p><table"
        END_TABLE = "</table>"

        if result.status_code != 200:
            warnings.warn("Website has not returned 200 status")
            return []

        lc_tmp = None
        raw_table = ""
        skip = True
        for line in result.iter_lines():
            line = line.decode()
            if skip:
                if line.strip().startswith(START_TABLE):
                    raw_table += line[len("<p>"):]
                    skip = False
                if lc and line.strip().startswith("<input type='hidden'"):
                    tmpdir_pattern = re.compile(
                        "<input type='hidden' name='tmpdir' value='(.*)'>")
                    tmpdir = tmpdir_pattern.match(line)
                    if tmpdir:
                        lc_tmp = tmpdir.group(1)

            else:
                if line.strip().startswith(END_TABLE):
                    break
                raw_table += line

        if not raw_table:
            warnings.warn("OgleIII query failed")
            return []

        soup = BeautifulSoup(raw_table, "lxml")
        table = soup.find('table')
        rows = table.findAll('tr')
        res_rows = []
        for tr in rows[1:]:
            cols = tr.findAll('td')
            res_cols = []
            for td in cols:
                res_cols.append(td.find(text=True))
            res_rows.append(res_cols)

        header = [th.find(text=True) for th in table.findAll("th")]
        return self._createStars(header, res_rows, lc_tmp)

    def _createStars(self, header, rows, lc_tmp):
        # [u'No', u'Field', u'StarID', u'RA', u'Decl', u'V', u'I', u'B']
        # [u'No', u'Field', u'StarID', u'RA', u'Decl', u'I']

        cols_map = self._parseHeader(header)
        stars = []
        for row in rows:
            field = str(row[cols_map.get("field")])
            starid = str(row[cols_map.get("starid")])
            ra = float(row[cols_map.get("ra")])
            dec = float(row[cols_map.get("dec")])

            identifiers = {}
            identifiers["Macho"] = row[cols_map.get("macho_id")]
            identifiers["Asas"] = row[cols_map.get("asas_id")]
            identifiers["OgleII"] = row[cols_map.get("ogle_ii_id")]
            identifiers["GCVS"] = row[cols_map.get("gcvs_id")]

            name = str(row[cols_map.get("name")])
            ident = {"OgleIII": {"name": name,
                                 "db_ident": {"field": field,
                                              "starid": starid}}}

            for ide, val in identifiers.items():
                if val != "\xa0":
                    ident[ide] = {"name": str(val)}

                    query_ide = self._parseDbNames(ide, val)
                    if query_ide:
                        ident[ide]["db_ident"] = query_ide

            more = {}
            for col in self.MORE:
                if cols_map.get(col) and cols_map.get(col):
                    val = row[cols_map.get(col)]
                    if val != "\xa0":
                        try:
                            val = float(val)
                        except:
                            val = str(val)

                        more[col] = val

            coo = (ra * 15, dec, "deg")

            st = Star(ident, name, coo, more)
            st.starClass = str(row[cols_map.get("type")])

            if lc_tmp:
                lc = self._getLc(name)
                if lc and len(lc) != 0:
                    st.putLightCurve(np.array(lc), meta=self.LC_META)

            stars.append(st)
        return stars

    def _parseHeader(self, header):
        cols_map = {}
        for i, col in enumerate(header):
            if col in list(self.COL_MAP.keys()):
                cols_map[self.COL_MAP[col]] = i
        return cols_map

    def _getLc(self, name):
        num = name.split("-")[-1][-2:]

        url = "%sdata/I/%s/%s.dat" % (self.ROOT, num, name)
        result = requests.get(url)

        if result.status_code == 200:
            star_curve = []
            for line in result.iter_lines():
                line = line.decode()
                parts = line.strip().split(" ")
                star_curve.append(
                    [round(float(parts[0]), 4), round(float(parts[1]), 3), round(float(parts[2]), 3)])
            return star_curve

    def _parseDbNames(self, db, name):
        if db == "Macho":
            parts = name.split(".")
            if len(parts) == 3:
                return {"Field": parts[0], "Tile": parts[1], "Seqn": parts[2]}

        elif db == "OgleII":
            parts = name.split("_")
            if len(parts) == 3:
                return {"field": parts[0]+"_"+parts[1], "starid" : parts[2]}

