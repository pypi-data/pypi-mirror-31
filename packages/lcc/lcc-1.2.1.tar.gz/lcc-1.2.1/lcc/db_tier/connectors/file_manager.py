import glob
import os

import numpy as np
from astropy.io import fits
from tqdm import tqdm

from lcc.db_tier.base_query import LightCurvesDb
from lcc.entities.exceptions import InvalidFilesPath, InvalidFile
from lcc.entities.light_curve import LightCurve
from lcc.entities.star import Star
from lcc.utils.output_process_modules import loadFromFile


# TODO: This class need to be upgraded
class FileManager(LightCurvesDb):
    """
    This class is responsible for managing light curve files

    Attributes
    -----------
    path : list, iterable
        Path key of folder of light curves .

    star_class : str
        Name of the loaded star-like type (e.g. Cepheids)

    suffix : str
        Suffix of light curve files in the folder. If suffix is "fits",
        files are loaded as fits files, otherwise files are considered
        as .dat files of light curve such as:

            #time    mag    err
            12    13.45    0.38

    files_limit : int, str
        Number of files which will be loaded

    db_ident : str
        Name of the database to which the file name will be assigned

        EXAMPLE:
            For the file "my_macho_star.dat" and given db_ident as "macho"
            makes Star object:

            star.ident["macho"] --> my_macho_star

    files_to_load : iterable of str
        List of file names which should be loaded from the given folder.
        If it is not specified all files will be loaded

    object_file_name : str
        Name of the pickle file which contains list of star objects
    """

    SUFFIXES = ["dat", "txt", "fits", "FITS"]
    DEFAULT_STARCLASS = "star"

    FITS_RA = "RA"
    FITS_DEC = "DEC"
    FITS_RA_UNIT = "RA_UN"
    FITS_DEC_UNIT = "DEC_UN"
    FITS_NAME = "IDENT"
    FITS_CLASS = "CLASS"
    DB_ORIGIN = "DB_ORIGIN"

    FITS_SUFFIX = ("fits", "FITS")

    BAD_VALUES = ("-99", "-99.0", "99", None, "N/A", np.NaN)
    TIME_COL = 0  # Order of columns in the light curve file
    MAG_COL = 1
    ERR_COL = 2
    ROUND_DIGITS = 3
    
    QUERY_OPTIONS = ["path"]

    def __init__(self, obtain_params):
        """
        Parameters
        ----------
        obtain_params : dict
            Query dictionary (see class Attributes doc above)
        """
        if isinstance(obtain_params, list) and len(obtain_params) == 1:
            obtain_params = obtain_params[0]

        path = obtain_params.get("path", None)

        if not path:
            raise IOError("Path %s was not found" % path)

        if isinstance(path, str):
            path = [path]

        self.path = path
        self.star_class = obtain_params.get(
            "star_class", self.DEFAULT_STARCLASS)
        self.suffix = obtain_params.get("suffix", None)
        file_lim = obtain_params.get("files_limit")
        if file_lim:
            self.files_limit = int(file_lim)
        else:
            self.files_limit = None
        self.db_ident = obtain_params.get("db_ident")
        self.files_to_load = obtain_params.get("files_to_load")
        self.object_file_name = obtain_params.get("object_file_name")

    def getStars(self, load_lc=True):
        """
        Common method for all stars provider

        If there are object_file_name in query dictionary, the object file
        of list of stars is loaded. In other case files from given path of
        the folder is loaded into star objects.

        Returns
        --------
        list of `Star` objects
            Star objects with light curves
        """

        if self.object_file_name:
            return self._load_stars_object()

        else:
            stars = []
            for path in self.path:
                stars += self._load_stars_from_folder(path)

        return stars

    def _load_stars_from_folder(self, path):
        """Load all files with a certain suffix as light curves"""

        if not path.endswith("/"):
            path += "/"

        # Get all light curve files (all files which end with certain suffix
        if not self.suffix:
            stars_list = []
            for suffix in self.SUFFIXES:
                stars_list += glob.glob("{}*{}".format(path, suffix))
        else:
            stars_list = glob.glob("{}*{}".format(path, self.suffix))

        found_files = len(stars_list)
        if found_files == 0:
            if self.suffix:
                raise InvalidFilesPath(
                    "There are no stars in %s with %s suffix" % (path, self.suffix))
            else:
                raise InvalidFilesPath(
                    "There are no stars in %s with any of supported suffix: %s" % (path, self.SUFFIXES))

        files_limit = self.files_limit or found_files

        if self.suffix in self.FITS_SUFFIX:
            return self._loadFromFITS(stars_list, files_limit)

        stars = self._loadDatFiles(
            [s for s in stars_list if s.endswith("dat")], files_limit)
        stars += self._loadFromFITS(
            [s for s in stars_list if s.endswith("fits")], files_limit)
        return stars

    def _loadDatFiles(self, star_paths, numberOfFiles):
        if not star_paths:
            return []
        stars = []
        counter = 1
        # Load every light curve and put it into star object
        for singleFile in tqdm(star_paths[:numberOfFiles], desc="Loading dat files:"):
            if self.files_to_load and os.path.basename(singleFile) not in self.files_to_load:
                break

            lc = LightCurve(self._loadLcFromDat(singleFile))

            # Check if light curve is not empty
            if (len(lc.mag) >= 1):
                db_ident = self.parseFileName(singleFile)
                if self.db_ident:
                    ident = {self.db_ident: {"name": db_ident}}
                else:
                    ident = {"file": {"name": db_ident}}

                star = Star(ident=ident)
                star.starClass = self.star_class

                star.putLightCurve(lc)
                stars.append(star)
            counter += 1
        return stars

    @classmethod
    def _loadLcFromDat(cls, file_name):
        """
        Load Light curve from dat file of light curve

        Parameters
        -----------
            file_with_path : str
                Name of the light curve file with its path

        Returns
        --------
            List of tuples of (time, mag, err)
        """

        try:
            dat = np.loadtxt(file_name, usecols=(
                cls.TIME_COL, cls.MAG_COL, cls.ERR_COL), skiprows=0)
        except IndexError:
            dat = np.loadtxt(file_name, usecols=(
                cls.TIME_COL, cls.MAG_COL, cls.ERR_COL), skiprows=2)

        except IOError as Argument:
            raise InvalidFilesPath(
                "\nCannot open light curve file\n %s" % Argument)

        mag, time, err = dat.T

        if not (len(mag) == len(time) == len(err)):
            raise InvalidFile(
                "Length of columns in light curve file is not the same")
        else:
            clean_dat = []
            for x, y, z in zip(mag, time, err):
                if (x not in cls.BAD_VALUES and y not in cls.BAD_VALUES and
                        z not in cls.BAD_VALUES):
                    clean_dat.append([round(x, cls.ROUND_DIGITS),
                                      round(y, cls.ROUND_DIGITS),
                                      round(z, cls.ROUND_DIGITS)])
            return clean_dat

    def _load_stars_object(self):
        """Load object file of list of stars"""

        stars = loadFromFile(os.path.join(self.path, self.object_file_name))

        if len(stars) == 0:
            raise InvalidFile("There are no stars in object file")
        if stars[0].__class__.__name__ != "Star":
            raise InvalidFile("It is not list of stars")

        return stars

    @staticmethod
    def parseFileName(file_path):
        """Return cleaned name of the star without path and suffix"""
        end = None
        if file_path.rfind(".") != -1:
            end = file_path.rfind(".")
        return file_path[file_path.rfind("/") + 1:end]

    def _loadFromFITS(self, star_paths, files_lim=None):
        if not star_paths:
            return []
        if files_lim and isinstance(files_lim, int):
            star_paths = star_paths[:files_lim]
        stars = []
        for path in tqdm(star_paths, desc="Loading FITS files:"):
            try:
                fits_file = fits.open(os.path.join(path))

            except Exception as e:
                raise InvalidFile("Invalid fits file or path: {}\n{}".format(self.path, e))

            stars.append(self._createStarFromFITS(fits_file))

        return stars

    @classmethod
    def _createStarFromFITS(self, fits):
        DB_NAME_END = "_name"
        DB_IDENT_SEP = "_id_"

        prim_hdu = fits[0].header

        ra = prim_hdu.get(self.FITS_RA)
        dec = prim_hdu.get(self.FITS_DEC)
        ra_unit = prim_hdu.get(self.FITS_RA_UNIT)
        dec_unit = prim_hdu.get(self.FITS_DEC_UNIT)

        star = Star(name=prim_hdu.get(self.FITS_NAME),
                    coo=(ra, dec, (ra_unit, dec_unit)),
                    starClass=prim_hdu.get(self.FITS_CLASS))

        ident = {}
        more = {}
        for db_name_key in list(prim_hdu.keys()):
            if db_name_key.endswith(DB_NAME_END):
                db_name = db_name_key[:-len(DB_NAME_END)]

                ident[db_name] = {}
                ident[db_name]["name"] = prim_hdu[db_name_key]

            elif DB_IDENT_SEP in db_name_key:
                db_name, ident_key = db_name_key.split(DB_IDENT_SEP)

                if not ident[db_name].get("db_ident"):
                    ident[db_name]["db_ident"] = {}

                ident[db_name]["db_ident"][ident_key] = prim_hdu[db_name_key]

            elif db_name_key not in ["SIMPLE", "BITPIX", "NAXIS", "EXTEND", self.FITS_RA, self.FITS_DEC, self.FITS_RA_UNIT, self.FITS_DEC_UNIT, self.FITS_NAME, self.FITS_CLASS]:
                more[db_name_key.lower()] = prim_hdu[db_name_key]

        star.ident = ident
        star.more = more

        for lc_hdu in fits[1:]:
            star.putLightCurve(self._createLcFromFits(lc_hdu))

        fits.close()
        return star

    @classmethod
    def _createLcFromFits(self, fits):
        time = []
        mag = []
        err = []
        for line in fits.data:
            if len(line) == 3:
                t, m, e = line
            elif len(line) == 2:
                t,m =line
                e = 0
            else:
                if hasattr(line, "__iter__"):
                    n = len(line)
                else:
                    n = None
                raise InvalidFile(
                    "Light curve binary extension of the fitst couldn't be parsed\nbecause of line {1}\n type: {0}, lenght: {2}".format(type(line), line, n))

            time.append(t)
            mag.append(m)
            err.append(e)

        meta = {"xlabel": fits.header.get("TTYPE1", None),
                "xlabel_unit": fits.header.get("TUNIT1", None),
                "ylabel": fits.header.get("TTYPE2", None),
                "ylabel_unit": fits.header.get("TUNIT2", None),
                "color": fits.header.get("FILTER", None),
                "origin": fits.header.get(self.DB_ORIGIN, None)
                }

        return LightCurve([time, mag, err], meta)

    @classmethod
    def writeToFITS(self, file_name, star, clobber=True):
        prim_hdu = fits.PrimaryHDU()

        prim_hdu.header["IDENT"] = star.name

        try:
            prim_hdu.header[self.FITS_RA] = star.coo.ra.degree
            prim_hdu.header[self.FITS_RA_UNIT] = "deg"
            prim_hdu.header[self.FITS_DEC] = star.coo.dec.degree
            prim_hdu.header[self.FITS_DEC_UNIT] = "deg"
            prim_hdu.header[self.FITS_CLASS] = star.starClass

        except AttributeError:
            pass

        for db, ident in star.ident.items():
            prim_hdu.header["HIERARCH " + db + "_name"] = ident["name"]

            identifiers = ident.get("db_ident")
            if not identifiers:
                identifiers = {}

            for key, value in identifiers.items():
                prim_hdu.header["HIERARCH " + db + "_id_" + key] = value

        for it, value in star.more.items():
            if len(it) > 8:
                it = "HIERARCH " + it
            prim_hdu.header[it] = value

        hdu_list = fits.HDUList(prim_hdu)

        for lc in star.light_curves:
            col1 = fits.Column(name=lc.meta.get("xlabel", "hjd"),
                                 unit=lc.meta.get("xlabel_unit", "days"),
                                 format='E', array=lc.time)
            col2 = fits.Column(name=(lc.meta.get("ylabel", "magnitude")),
                                 unit=lc.meta.get("ylabel_unit", "mag"),
                                 format='E', array=lc.mag)
            col3 = fits.Column(name="error",
                                 unit=lc.meta.get("ylabel_unit", "mag"),
                                 format='E', array=lc.err)

            lc_hdu = fits.BinTableHDU.from_columns([col1, col2, col3])
            # lc_hdu = fits.new_table(fits.ColDefs([col1, col2, col3]))

            lc_hdu.header["FILTER"] = lc.meta.get("color", "")
            lc_hdu.header[
                "HIERARCH " + self.DB_ORIGIN] = lc.meta.get("origin", "")

            hdu_list.append(lc_hdu)

        hdu_list.writeto(
            file_name, overwrite=clobber)
