from typing import Any, Dict, List, Type

import attr
from braceexpand import braceexpand
from fastapi import FastAPI, Query, Request
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from morecantile import TileMatrixSet
from rio_tiler.constants import WEB_MERCATOR_TMS
from rio_tiler.errors import InvalidBandName
from rio_tiler.io import BaseReader, MultiBandReader, Reader
from rio_tiler.models import BandStatistics, ImageData, Info, PointData
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

@attr.s
class MultiFilesBandsReader(MultiBandReader):
    """Multiple Files as Bands."""

    input: Any = attr.ib()
    tms: TileMatrixSet = attr.ib(default=WEB_MERCATOR_TMS)

    reader_options: Dict = attr.ib(factory=dict)
    reader: Type[BaseReader] = attr.ib(default=Reader)

    files: List[str] = attr.ib(init=False)

    minzoom: int = attr.ib()
    maxzoom: int = attr.ib()

    @minzoom.default
    def _minzoom(self):
        return self.tms.minzoom

    @maxzoom.default
    def _maxzoom(self):
        return self.tms.maxzoom

    def __attrs_post_init__(self):
        """Fetch Reference band to get the bounds."""
        self.files = list(braceexpand(self.input))
        print(self.files)
        self.bands = [f"b{ix + 1}" for ix in range(len(self.files))]

        with self.reader(self.files[0], tms=self.tms, **self.reader_options) as cog:
            self.bounds = cog.bounds
            self.crs = cog.crs
            self.minzoom = cog.minzoom
            self.maxzoom = cog.maxzoom

    def _get_band_url(self, band: str) -> str:
        """Validate band's name and return band's url."""
        if band not in self.bands:
            raise InvalidBandName(f"{band} is not valid")

        index = self.bands.index(band)
        return self.files[index]


def DatasetPathParams(url: str = Query(..., description="Dataset URL"), request: Request = None) -> List[str]:
    """Create dataset path from args"""
    try:
        raw_url = str(request.url).split("?url=")
        print(f"--------- {raw_url}")
        if "info" in raw_url[1] or "tilejson.json" in raw_url:
            first_asset = list(braceexpand(raw_url[-1]))[0]
            print(f"**** {first_asset}")
            return first_asset
        else:
            #print(f"----url----- {url}")
            return url
    except:
        return url
