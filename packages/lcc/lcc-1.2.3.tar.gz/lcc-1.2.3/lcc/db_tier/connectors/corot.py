

import io
import collections
import os
import warnings

import numpy as np
from astropy.io import fits
import requests

from lcc.db_tier.base_query import LightCurvesDb
from lcc.db_tier.vizier_tap_base import VizierTapBase
from lcc.entities.light_curve import LightCurve
from lcc.utils.data_analysis import to_ekvi_PAA


class CorotBright(VizierTapBase, LightCurvesDb):
    """
    CoRoT connector. TAP query and downloading of the light curve fits are
    executed on Vizier catalog. It inherits `VizierTapBase` - see
    documentation of this class to class attributes description.

    As for all TAP queries it is possible to use "<" and ">" marks (for example
    {"CoRot":">2.5}).

    EXAMPLES
    ---------
    queries = [{"ra": 102.707, "dec": -0.54089, "delta": 10},
               {"CoRot": 116}]
    client = StarsProvider.getProvider("CorotBright", queries)
    stars = client.getStars(max_bins=10000)
    """

    LC_URL = "http://vizier.u-strasbg.fr/viz-bin/nph-Cat?-plus=-%2b&B/corot/files/"
    TABLE = "B/corot/Bright_star"

    LC_FILE = "FileName"

    LC_META = {"xlabel": "Terrestrial time",
               "xlabel_unit": "days",
               "ylabel": "Flux",
               "ylabel_unit": "Electrons per second",
               "color": "No",
               "origin": "CoRoT",
               "invert_yaxis": False}

    IDENT_MAP = collections.OrderedDict(
        (("VizierDb", "Star"), ("CorotBright", "CoRoT")))
    MORE_MAP = collections.OrderedDict((("(B-V)", "b_v_mag"),
                                        ("SpT", "spectral_type"),
                                        ("Vmag", "v_mag"),
                                        ("VMAG", "abs_v_mag"),
                                        ("Teff", "temp")))

    QUERY_OPTIONS = ["ra", "dec", "delta", "nearest", "CoRot"]

    def _getLightCurve(self, file_name, max_bins=1e3, *args, **kwargs):
        """
        Obtain light curve

        Parameters
        -----------
        file_name : str
            Path to the light curve file from root url

        max_bins : int
            Maximal number of dimension of the light curve

        Returns
        --------
        tuple
            Tuple of times, magnitudes, errors lists
        """
        EXT_NUM = 2

        warnings.warn("""COROT: Downloading super huge light curves from this
        database can take few minutes...""")
        response = requests.get(os.path.join(self.LC_URL, file_name))
        lcs = []
        with fits.open(io.BytesIO(response.content)) as f:
            for extension in f[1:EXT_NUM]:
                raw_lc = self._createFromExtension(extension, max_bins)
                if raw_lc:
                    lcs.append(LightCurve(raw_lc, self.LC_META))

        return lcs

    def _createFromExtension(self, extension, max_bins):
        time = []
        mag = []
        err = []
        error_occured = False
        for line in extension.data:
            try:
                time.append(line[self.TIME_COL])
                mag.append(line[self.MAG_COL])
                err.append(line[self.ERR_COL] / self.ERR_MAG_RATIO)
            # Case of no lc
            except IndexError:
                error_occured = True

        if error_occured:
            if len(time) == len(mag) and len(time) > 0:
                if not err or len(err) != len(time):
                    err = np.zeros(len(time))
            else:
                return None

        if len(time) > max_bins:
            red_time, red_mag = to_ekvi_PAA(time, mag, bins=max_bins)
            red_time, red_err = to_ekvi_PAA(time, err, bins=max_bins)
        else:
            return time, mag, err
        return red_time, red_mag, red_err

    def get_name(self, star_info):
        return star_info.get("Star", "CoRoT")


class CorotFaint(CorotBright):
    """
    Corot archive of faint stars

    Examples
    ---------
    queries = [ { "CoRot" : "102706554"},
                {"ra": 100.94235, "dec" : -00.89651, "delta" : 10}]        
    client = StarsProvider().getProvider("CorotFaint", queries)
    stars = client.getStars(max_bins = 10000 )    
    """

    TABLE = "B/corot/Faint_star"
    IDENT_MAP = {"CorotFaint": "CoRoT"}

    MORE_MAP = collections.OrderedDict((("SpT", "spectral_type"),
                                        ("Vmag", "v_mag"),
                                        ("Rmag", "r_mag"),
                                        ("Bmag", "b_mag"),
                                        ("Imag", "i_mag"),
                                        ("Gmean", "g_mag")))

    LC_META = {"xlabel": "Barycentric time",
               "xlabel_unit": "julian days",
               "ylabel": "Flux",
               "ylabel_unit": "Electrons per 32 second",
               "color": "R",
               "invert_yaxis": False}

    TIME_COL = 2
    MAG_COL = 4
    ERR_COL = 5

    ERR_MAG_RATIO = 16.
