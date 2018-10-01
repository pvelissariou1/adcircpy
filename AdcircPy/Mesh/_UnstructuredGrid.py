from collections import defaultdict
import numpy as np
from matplotlib.tri import Triangulation
import matplotlib.pyplot as plt
from matplotlib.path import Path
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.cm import ScalarMappable
from scipy.interpolate import griddata
import pyproj
from haversine import haversine
from AdcircPy import demtools

def get_xyz(self, extent=None, epsg=None):
  if extent is None:
    extent = self.get_extent()
  if epsg is None:
    epsg = self.epsg
  idx = self._get_extent_idx(extent, epsg)
  return np.vstack((self.x[idx], self.y[idx], self.values[idx])).T

def get_xy(self, extent=None, epsg=None):
  if extent is None:
    extent = self.get_extent()
  if epsg is None:
    epsg = self.epsg
  idx = self._get_extent_idx(extent, epsg)
  return np.vstack((self.x[idx], self.y[idx])).T

def transform_to_epsg(self, epsg):
  self_proj = pyproj.Proj(init="epsg:{}".format(self.epsg))
  target_proj = pyproj.Proj(init="epsg:{}".format(epsg))
  x, y = pyproj.transform(self_proj, target_proj, self.x, self.y)
  self.x = np.asarray(x).flatten()
  self.y = np.asarray(y).flatten()
  self.epsg = epsg

def _init_Tri(self):
  if np.ma.is_masked(self._values):
    trimask = np.any(self._values.mask[self.elements], axis=1)
    self._Tri = Triangulation(self.x, self.y, self.elements, trimask)
  else:
    self._Tri = Triangulation(self.x, self.y, self.elements)


def make_plot(self, extent=None, epsg=None, axes=None, title=None, show=False, **kwargs):
  # print(self.va)
  total_colors=256
  self._init_fig(axes, extent, title, epsg)
  self._vmin = kwargs.pop("vmin", np.min(self._values))
  self._vmax = kwargs.pop("vmax", np.max(self._values))
  self._cmap = kwargs.pop("cmap", "jet")
  self._levels = kwargs.pop("levels", np.linspace(self._vmin, self._vmax, total_colors))
  self._axes.tricontourf(self._Tri, self._values, levels=self._levels, cmap=self._cmap, extend='both')
  self._init_cbar(self._cmap, self._vmin, self._vmax)
  cbar_label=None
  if cbar_label is not None:
    self._cbar.set_label(cbar_label)
  self._cbar.set_ticks([self._vmin,
                  self._vmin+(1./4.)*(self._vmax-self._vmin),
                  self._vmin+(1./2.)*(self._vmax-self._vmin),
                  self._vmin+(3./4.)*(self._vmax-self._vmin),
                  self._vmax])
  self._cbar.set_ticklabels([np.around(self._vmin, 2), 
                          np.around(self._vmin+(1./4.)*(self._vmax-self._vmin), 2),
                          np.around(self._vmin+(1./2.)*(self._vmax-self._vmin), 2),
                          np.around(self._vmin+(3./4.)*(self._vmax-self._vmin), 2),
                          np.around(self._vmax, 2)])
  
  if show == True:
    plt.show()

  return self._axes

def plot_velocity(self, **kwargs):
    raise NotImplementedError("Coming soon!")
    start_timestep = kwargs.pop('start_timestep', 0)
    stop_timestep  = kwargs.pop('stop_timestep', len(self.time))
    if axes is None:                
        fig = plt.figure()
        axes  = fig.add_subplot(111)
    ax = axes.quiver(self.x, self.y, self.u[0,:], self.v[:,0], vmin=vmin, vmax=vmax, **kwargs)
    axes.axis('scaled')
    def update(i):
       ax.set_array(self.Dataset['zs'][i,:-1,:-1].ravel())
       return ax
    
    anim = FuncAnimation(fig, update, frames=np.arange(start_timestep+1, stop_timestep), interval=interval)
    if colorbar==True:
        plt.colorbar(ax)
    if show is True:
        plt.show()
    return anim

def get_difference(self, other, step=0):
    

    if isinstance(self.values, list):
        self_values = self.values[step]
    else:
        self_values = self.values

    if isinstance(other.values, list):
        other_values = other.values[step]
    else:
        other_values = other.values

    if np.ma.is_masked(self_values):
        self_values = np.ma.filled(self_values, 0.)

    if np.ma.is_masked(other.values):
        other_values = np.ma.filled(other_values, 0.)
    values = self_values - other_values
    # values = np.ma.masked_equal(values, 0.)
    kwargs = self.get_dict()
    kwargs['values'] = values
    return Surface.SurfaceDifference(**kwargs)

def get_mean_value(self, **kwargs):
    epsg   = kwargs.pop("epsg", self.epsg)
    extent = kwargs.pop("extent", self.get_extent(epsg=epsg))
    step   = kwargs.pop("step", 0)
    idx = self.get_extent_idx(extent, epsg)
    if isinstance(self.values, list):
        values = self.values[step]
    else:
        values = self.values
    return np.nanmean(values[idx])

def plot_diff(self, extent=None, epsg=None, axes=None, vmin=None, vmax=None, title=None, **kwargs):
    axes, idx = _fig.init_fig(self, axes, extent, title, epsg)
    if vmin is None:
        vmin = np.min(self.values[idx])
    if vmax is None:
        np.max(self.values[idx])

    cmap = plt.get_cmap(kwargs.pop("cmap", "seismic"))
    levels = kwargs.pop("levels", np.linspace(np.min(self.values[idx]), np.max(self.values[idx]), 256))
    norm = _fig.FixPointNormalize(sealevel=0, vmax=vmax, vmin=vmin, col_val=0.5)
    if np.ma.is_masked(self.values):
        trimask = np.any(self.values.mask[self.elements], axis=1)
        Tri = Triangulation(self.x, self.y, self.elements, trimask)
        axes.tricontourf(Tri, self.values, levels=levels, cmap=cmap, extend='both', norm=norm)
    else:
        axes.tricontourf(self.x, self.y, self.elements, self.values, levels=levels, cmap=cmap, extend='both', norm=norm)
    cbar = self._init_cbar(axes, cmap, vmin, vmax)
    cbar.set_ticks([vmin, vmin + 0.5*(vmax-vmin), vmax])
    cbar.set_ticklabels([np.around(vmin, 2), 0.0, np.around(vmax, 2)])
    cbar.set_label(r'elevation [$\Delta$ m]')
    return axes

def rasterize_to_geoTransform(self, geoTransform, shape, **kwargs):
    """
    Converts an ADCIRC mesh object into a ADCIRC raster object.
    With this

    Parameters
    ----------
    geoTransform : tuple
        geoTransform[0] /* top left x */
        geoTransform[1] /* west-east pixel resolution */
        geoTransform[2] /* 0 */
        geoTransform[3] /* top left y */
        geoTransform[4] /* 0 */
        geoTransform[5] /* north-south pixel resolution (negative value) */

    xpixels : int
        Description of arg2

    ypixels : int

    Returns
    -------
    raster object
        Can be used to export to geoTif, and other operations such as filtering.
    """
    epsg = kwargs.pop("epsg", self.epsg)
    padding = kwargs.pop("padding", None)
    xpixels, ypixels = shape
    x = np.linspace(geoTransform[0], geoTransform[0] + xpixels*geoTransform[1], xpixels)
    y = np.linspace(geoTransform[3] + ypixels*geoTransform[5], geoTransform[3], ypixels)
    xt, yt = np.meshgrid(x, y)
    xt = xt.reshape(xt.size)
    yt = np.flipud(yt.reshape(yt.size))
    xyt = np.vstack((xt,yt)).T
    # create path object of target bounding box
    bbox_path = Path([(np.min(xt), np.min(yt)),
                    (np.max(xt), np.min(yt)),
                    (np.max(xt), np.max(yt)),
                    (np.min(xt), np.max(yt)),
                    (np.min(xt), np.min(yt))], closed=True)
    # interpolate mesh information to bounding box grid.
    xyz = self.get_xyz(extent=bbox_path)
    zt = griddata((xyz[:,0], xyz[:,1]), xyz[:,2], (xt, yt), method='linear', fill_value=np.nan)
    # Generate boundary masks.
    outerBoundary = self.build_outer_polygon()
    outerBoundary = outerBoundary.clip_to_bbox((np.min(xt), np.min(yt), np.max(xt), np.max(yt)))
    mask = np.logical_or(np.isin(zt, np.nan), ~outerBoundary.contains_points(xyt))
    zt = np.ma.masked_array(zt, mask)
    innerBoundaries = self.build_inner_polygons()
    for innerBoundary in innerBoundaries:
        if outerBoundary.intersects_path(innerBoundary):
            innerBoundary = innerBoundary.clip_to_bbox((np.min(xt), np.min(yt), np.max(xt), np.max(yt)))
            mask = np.logical_or(zt.mask, innerBoundary.contains_points(xyt))
            zt = np.ma.masked_array(zt.data, mask)
    #TODO: Compound mask for other boundaries.
    if self.weir_boundaries is not None:
        for boundary in self.weir_boundaries:
            pass
    if self.culvert_boundaries is not None:
        for boundary in self.culvert_boundaries:
            pass
    if padding is not None:
        padding = griddata((padding[:,0], padding[:,1]), padding[:,2], (xt, yt), method='nearest')
        idx, = np.where(zt.mask)
        zt = np.ma.filled(zt, np.nan)
        zt[idx] = padding[idx]
    zt = zt.reshape(shape)
    return demtools.DEM(x, y, zt, geoTransform, self.epsg, self.datum)

def get_raster_from_extent(self, extent , dx, dy, epsg, padding=None):
    """
    This script rasterizes the mesh into a regular grid that can be exported as GeoTiff.
    Uselful for exploring the data on a GIS program.
    """
    min_x, max_x, min_y, max_y = extent
    
    x = np.arange(min_x, max_x+dx, dy)
    y = np.arange(min_y, max_y+dy, dy)
    
    xt, yt = np.meshgrid(x, y)
    shape = xt.shape
    
    xt = xt.reshape(xt.size)
    yt = np.flipud(yt.reshape(yt.size))
    xyt = np.vstack((xt,yt)).T

    bbox_path = Path([(np.min(xt), np.min(yt)),
                    (np.max(xt), np.min(yt)),
                    (np.max(xt), np.max(yt)),
                    (np.min(xt), np.max(yt)),
                    (np.min(xt), np.min(yt))], closed=True)

    xyz = self.get_xyz(extent=bbox_path, radius=0.2)
    zt = griddata((xyz[:,0], xyz[:,1]), xyz[:,2], (xt, yt), method='linear', fill_value=np.nan)
    
    
    # generate masks
    if ~hasattr(self,'outer_boundary'):
        self.outer_boundary = self.build_outer_polygon()
    path = self.outer_boundary.clip_to_bbox((np.min(xt), np.min(yt), np.max(xt), np.max(yt)))
    mask1 = np.isin(zt, -99999.0)
    mask2 = path.contains_points(xyt)
    mask = np.logical_or(mask1, ~mask2)
    for i in range(len(self.land_boundaries)):
        if self.land_boundaries[i][-1] in [1,21]:
            extents = self.land_boundaries[i][0].get_extents()
            extents = extents.get_points()
            c1 = np.logical_and(np.min(xt) <= extents[1,0], np.max(xt) >= extents[0,0])
            c2 = np.logical_and(np.min(yt) <= extents[1,1], np.max(yt) >= extents[0,1])
            if np.logical_and(c1,c2):
                shape = self.land_boundaries[i][0].clip_to_bbox((np.min(xt), np.min(yt), np.max(xt), np.max(yt)))
                mask3 = shape.contains_points(xyt)
                mask = np.logical_or(mask, mask3)  
    geoTransform = (np.min(min_x), dx, 0, np.max(y), 0, -np.abs(dy))
    depth = np.ma.masked_array(zt, mask).reshape(_shape)
    if padding is not None:
        depth = adcpy.adcirc.raster._apply_padding(x, y, depth, padding)
    DEM = demtools.DEM()
    return DEM(x, y, depth, geoTransform, 4326, self.datum)

def get_contours(self, levels, **kwargs):
    epsg = kwargs.pop("epsg", self.epsg)

    if epsg != self.epsg:
        self_proj   = pyproj.Proj(init='epsg:{}'.format(self.epsg))
        target_proj = pyproj.Proj(init='epsg:{}'.format(epsg))
        x, y = pyproj.transform(self_proj, target_proj, self.x, self.y)

    else:
        x = self.x
        y = self.y

    if np.ma.is_masked(self.values):
        mask = np.where(self.values.mask)
        trimask = np.any(np.in1d(self.elements, mask).reshape(-1, 3), axis=1)
        Tri = Triangulation(x, y, self.elements, trimask)
    else:
        Tri = Triangulation(x, y, self.elements)
    fig = plt.figure()
    axes = fig.add_subplot(111)
    ax = axes.tricontour(Tri, self.values, levels=levels)
    plt.close(fig)

    contours = defaultdict(list)
    for i, LineCollection in enumerate(ax.collections):
        for Path in LineCollection.get_paths():
            contours[ax.levels[i]].append(Path)
    return dict(contours)

def get_values_at_xy(self, x, y, step=0, method='linear'):
    if isinstance(self.values, list):
        values = self.values[step]
    else:
        values = self.values
    if np.ma.is_masked(values):
        values = np.ma.filled(values, 0.0)
    elif np.isin(values, -99999.0).any():
        idx = np.where(np.isin(values, -99999.0))
        values[idx] = 0.0    
    if method != 'force':
        return griddata((self.x,self.y),values,(x,y), method=method)
    else:
        idx = np.where(~np.isin(values, 0.0))
        return griddata((self.x[idx], self.y[idx]), values[idx], (x, y), method='nearest')

def get_finite_volume_element_list(self, index):
    return self.elements[np.where(np.any(np.isin(self.elements, index), axis=1))[0]]

def get_finite_volume_Path_list(self, index):
    return [self.get_Path_from_element(element) for element in self.get_finite_volume_element_list(index)]

def get_element_containing_coord(self, coord):
    x = coord[0]; y = coord[1]
    distance, node_idx = self.KDTree.query([x,y])
    elements = self.get_finite_volume_Path_list(node_idx)
    for i, element in enumerate(elements):
        if element.contains_point((x,y)):
            return self.get_finite_volume_element_list(node_idx)[i]

def _init_fig(self, axes=None, extent=None, title=None, epsg=None):
  if axes is None:                
    fig = plt.figure()
    axes  = fig.add_subplot(111)
  if title is not None:
    axes.set_title(title)
  if extent is None:
    extent = self.get_extent()
  if epsg is None:
    epsg = self.epsg
    idx  = self._get_extent_idx(extent, epsg)
    axes.axis('scaled')
    axes.axis(extent) 
  self._axes=axes
  self._idx=idx

def _init_cbar(self, cmap, vmin, vmax):
  divider = make_axes_locatable(self._axes)
  cax     = divider.append_axes("bottom", size="2%", pad=0.5)
  mappable = ScalarMappable(cmap=cmap)
  mappable.set_array([])
  mappable.set_clim(vmin, vmax)
  self._cbar = plt.colorbar(mappable, cax=cax, extend='both', orientation='horizontal')

def get_extent(self, **kwargs):
    epsg = kwargs.pop("epsg", self.epsg)

    if epsg != self.epsg:
        self_proj = pyproj.Proj(init="epsg:{}".format(self.epsg))
        target_proj = pyproj.Proj(init="epsg:{}".format(epsg))
        x, y = pyproj.transform(self_proj, target_proj, self.x, self.y)
    else:
        x = self.x
        y = self.y

    return [np.min(x), np.max(x), np.min(y), np.max(y)]

def _get_extent_idx(self, extent, epsg, **kwargs):
    # epsg   = kwargs.pop("epsg", self.epsg)
    # extent = kwargs.pop("extent", self.get_extent(epsg=epsg))
    if epsg != self.epsg:
        self_proj = pyproj.Proj(init="epsg:{}".format(self.epsg))
        target_proj = pyproj.Proj(init="epsg:{}".format(epsg))
        x, y = pyproj.transform(self_proj, target_proj, self.x, self.y)
    else:
        x = self.x
        y = self.y
    if isinstance(extent, list) or isinstance(extent, tuple):
        bound_box = np.logical_and(
                        np.logical_and(x>=extent[0], x<=extent[1]),
                        np.logical_and(y>=extent[2], y<=extent[3]))
        idx, = np.where(bound_box)
    elif isinstance(extent, Path):
        idx, = np.where(extent.contains_points(np.vstack((x,y)).T))
    return idx

def plot_trimesh(self, extent=None, axes=None, title=None, color='black', linewidth=0.5, alpha=0.4):
    axes, idx = fig._init_fig(self, axes, extent, title)
    axes.triplot(self.x, self.y, self.elements, color=color, linewidth=linewidth, alpha=alpha)
    return axes

def get_finite_volume(self, index):
    self.get_elements_from_
    return Path.make_compound_path(*paths)


def get_Path_from_element(self, element):
    return Path([[self.x[element[0]], self.y[element[0]]],
                 [self.x[element[1]], self.y[element[1]]],
                 [self.x[element[2]], self.y[element[2]]],
                 [self.x[element[0]], self.y[element[0]]]], closed=True)
    





def get_elements_in_extent(self, extent):
    if extent is None: extent = self.get_extent()
    mask_x  = np.logical_and(self.x > extent[0], self.x < extent[1])
    mask_y  = np.logical_and(self.y > extent[2], self.y < extent[3])
    masked  = np.ma.masked_where(np.logical_and(mask_x, mask_y), self.values)
    trimask = np.all(masked.mask[self.elements], axis=1)
    idx,  = np.where(trimask) 
    paths = list()
    for i in idx:
        vertex = list()
        codes = [Path.MOVETO]
        for j in [0,1,2]:
            vertex.append((self.x[self.elements[i][j]], self.y[self.elements[i][j]]))
            codes.append(Path.LINETO)
        vertex.append(vertex[0])
        codes[-1] = Path.CLOSEPOLY
        paths.append(Path(vertex, codes))
    return paths

def _get_finite_volume_interp(self, idx, radius=None):
    midpoints = list()
    centroids = list()
    adjacent_elements = self.get_elements_surrounding_node(idx)
    # Iterate over surrounding elements
    for j, element in enumerate(adjacent_elements):
        _element = list(element)
        _element.append(_element[0])
        _midpoints = list()
        # Calculate element midpoints and centroid
        for i, point_idx in enumerate(element):         
            dx =  self.x[_element[i+1]] - self.x[_element[i]]
            dy =  self.y[_element[i+1]] - self.y[_element[i]]
            if np.isin(idx, [_element[i], _element[i+1]]):
                midpoints.append((self.x[_element[i]] + 0.5*dx, self.y[_element[i]] + 0.5*dy))
            _midpoints.append((self.x[_element[i]] + 0.5*dx, self.y[_element[i]] + 0.5*dy))
        _midpoints = np.array(_midpoints)
        centroids.append((np.mean(_midpoints[:,0]),np.mean(_midpoints[:,1])))
        _element = list(element)
        while _element[0] != idx:
            _element = list(np.roll(_element,1))
        adjacent_elements[j] = _element
    adjacent_elements = np.array(adjacent_elements)
    lateral_indexes, counts = np.unique(adjacent_elements, return_counts=True)
    vertices = list()
    for centroid in centroids:
        vertices.append(centroid)
    for midpoint in midpoints:
        vertices.append(midpoint)    
    ordered_vertices = list()
    if 1 in counts: # means that this node is at a boundary and need to be included in the polygon.
        ordered_vertices.append((self.x[idx], self.y[idx]))
        index = list(np.delete(lateral_indexes, np.where(counts>1))).pop()
        x = self.x[idx]
        y = self.y[idx]
        dx = self.x[index] - self.x[idx]
        dy = self.y[index] - self.y[idx]
        ordered_vertices.append(vertices.pop(vertices.index((x+0.5*dx,y+0.5*dy))))
    else: # means that this is node is fully surrounded by elements so the obs point is not included in polygon.
        ordered_vertices.append(vertices.pop())
    lon = ordered_vertices[-1][0]
    lat = ordered_vertices[-1][1]
    while vertices:
        diff = list()
        for vertex in vertices:
            _diff = haversine((vertex[1], vertex[0]), (lat, lon))
            diff.append(_diff)
        ordered_vertices.append(vertices.pop(diff.index(min(diff))))
        lon = ordered_vertices[-1][0]
        lat = ordered_vertices[-1][1]
    ordered_vertices.append(ordered_vertices[0])
    return Path(ordered_vertices, closed=True)

def _init_datum_grid(self):
  if self._datum_grid is not None:
    with open(self._datum_grid, 'r') as f: 
      f.readline().rstrip()
      original_datum, target_datum = f.readline().split(':')
      if original_datum == self.datum:
        NP = int(f.readline().split()[1])
        values = list()
        for k in range(NP):
          values.append(float(f.readline().split()[3]))
        self.original_mesh_values = self.values
        self.original_mesh_datum = self.datum
        self._values += np.asarray(values)
        self.datum = target_datum


# def get_dict(self):
#     return {  'x'                   : self.x,
#               'y'                   : self.y,
#               'elements'            : self.elements,
#               'values'              : self.values,
#               'nodeID'              : self.nodeID,
#               'elementID'           : self.elementID, 
#               "ocean_boundaries"    : self.ocean_boundaries,
#               "land_boundaries"     : self.land_boundaries,
#               "inner_boundaries"    : self.inner_boundaries,
#               "weir_boundaries"     : self.weir_boundaries,
#               "inflow_boundaries"   : self.inflow_boundaries,
#               "outflow_boundaries"  : self.outflow_boundaries,
#               "culvert_boundaries"  : self.culvert_boundaries}