"""Plotting

Plotting functions for each tool and toplevel plotting functions for AnnData.
"""

import numpy as np
import pandas as pd
from pandas.api.types import is_categorical_dtype
import networkx as nx
from scipy.sparse import issparse
from matplotlib import pyplot as pl
from matplotlib.colors import is_color_like
from matplotlib import rcParams

from .. import utils
from ... import utils as sc_utils
from ... import settings
from ... import logging as logg
from ..anndata import scatter, ranking
from ..utils import matrix
from ..utils import timeseries, timeseries_subplot, timeseries_as_heatmap

# ------------------------------------------------------------------------------
# Visualization tools
# ------------------------------------------------------------------------------


def pca(adata, **params):
    """Plot PCA results.

    The parameters are the ones of the scatter plot. Call pca_ranking separately
    if you want to change the default settings.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    use_raw : `bool`, optional (default: `True`)
        Use `raw` attribute of `adata` if present.
    sort_order : `bool`, optional (default: `True`)
        For continuous annotations used as color parameter, plot data points
        with higher values on top of others.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    components : str or list of str, optional (default: '1,2')
         String of the form '1,2' or ['1,2', '2,3'].
    projection : {'2d', '3d'}, optional (default: '2d')
         Projection of plot.
    legend_loc : str, optional (default: 'right margin')
         Options for keyword argument 'loc'.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    """
    show = params['show'] if 'show' in params else None
    if 'show' in params: del params['show']
    pca_scatter(adata, **params, show=False)
    pca_loadings(adata, show=False)
    pca_variance_ratio(adata, show=show)


def pca_scatter(
        adata,
        color=None,
        use_raw=True,
        sort_order=True,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None,
        ax=None):
    """Scatter plot in PCA coordinates.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    layout : {'fr', 'drl', ...}, optional (default: last computed)
        One of the `draw_graph` layouts, see sc.tl.draw_graph. By default,
        the last computed layout is taken.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    use_raw : `bool`, optional (default: `True`)
        Use `raw` attribute of `adata` if present.
    sort_order : `bool`, optional (default: `True`)
        For continuous annotations used as color parameter, plot data points
        with higher values on top of others.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    components : str or list of str, optional (default: '1,2')
         String of the form '1,2' or ['1,2', '2,3'].
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object.

    Returns
    -------
    If `show==False`, a list of `matplotlib.Axis` objects. Every second element
    corresponds to the 'right margin' drawing area for color bars and legends.
    """
    axs = scatter(
        adata,
        basis='pca',
        color=color,
        use_raw=use_raw,
        sort_order=sort_order,
        alpha=alpha,
        groups=groups,
        components=components,
        projection=projection,
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
        legend_fontweight=legend_fontweight,
        color_map=color_map,
        palette=palette,
        right_margin=right_margin,
        size=size,
        title=title,
        show=False,
        save=False, ax=ax)
    utils.savefig_or_show('pca_scatter', show=show, save=save)
    if show == False: return axs


def pca_loadings(adata, components=None, show=None, save=None):
    """Rank genes according to contributions to PCs.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    components : str or list of integers, optional
        For example, ``'1,2,3'`` means ``[1, 2, 3]``, first, second, third
        principal component.
    show : bool, optional (default: None)
        Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    """
    if components is None: components = [1, 2, 3]
    elif isinstance(components, str): components = components.split(',')
    components = np.array(components) - 1
    ranking(adata, 'varm', 'PCs', indices=components)
    utils.savefig_or_show('pca_loadings', show=show, save=save)


def pca_variance_ratio(adata, log=False, show=None, save=None):
    """Plot the variance ratio.

    Parameters
    ----------
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    """
    ranking(adata, 'uns', 'variance_ratio', dictionary='pca', labels='PC', log=log)
    utils.savefig_or_show('pca_variance_ratio', show=show, save=save)


def diffmap(
        adata,
        color=None,
        use_raw=True,
        sort_order=True,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None, ax=None):
    """Scatter plot in Diffusion Map basis.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    use_raw : `bool`, optional (default: `True`)
        Use `raw` attribute of `adata` if present.
    sort_order : `bool`, optional (default: `True`)
        For continuous annotations used as color parameter, plot data points
        with higher values on top of others.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    components : str or list of str, optional (default: '1,2')
         String of the form '1,2' or ['1,2', '2,3'].
    projection : {'2d', '3d'}, optional (default: '2d')
         Projection of plot.
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors cycle to use for categorical groups.
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object. Only works if plotting a single component.
    """
    if components == 'all':
        components_list = ['{},{}'.format(*((i, i+1) if i % 2 == 1 else (i+1, i)))
            for i in range(1, adata.obsm['X_diffmap'].shape[1])]
    else:
        if components is None: components = '1,2' if '2d' in projection else '1,2,3'
        if not isinstance(components, list): components_list = [components]
        else: components_list = components
    for components in components_list:
        axs = scatter(
            adata,
            basis='diffmap',
            color=color,
            use_raw=use_raw,
            sort_order=sort_order,
            alpha=alpha,
            groups=groups,
            components=components,
            projection=projection,
            legend_loc=legend_loc,
            legend_fontsize=legend_fontsize,
            legend_fontweight=legend_fontweight,
            color_map=color_map,
            palette=palette,
            right_margin=right_margin,
            size=size,
            title=title,
            show=False,
            save=False,
            ax=ax)
        writekey = 'diffmap'
        if isinstance(components, list): components = ','.join(
            [str(comp) for comp in components])
        writekey += ('_components' + components.replace(',', '')
                     + (save if isinstance(save, str) else ''))
        if settings.autosave or (save is not None):
            utils.savefig(writekey)
    show = settings.autoshow if show is None else show
    if not settings.autosave and show: pl.show()
    if show == False: return axs


def draw_graph(
        adata,
        edges=False,
        edges_width=0.1,
        edges_color='grey',
        layout=None,
        color=None,
        use_raw=True,
        sort_order=True,
        alpha=None,
        groups=None,
        components=None,
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None,
        ax=None):
    """Scatter plot in graph-drawing basis.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    edges : `bool`, optional (default: `False`)
        Show edges.
    edges_width : `float`, optional (default: 0.1)
        Width of edges.
    edges_color : matplotlib color, optional (default: 'grey')
        Color of edges.
    layout : {'fr', 'drl', ...}, optional (default: last computed)
        One of the `draw_graph` layouts, see sc.tl.draw_graph. By default,
        the last computed layout is taken.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    use_raw : `bool`, optional (default: `True`)
        Use `raw` attribute of `adata` if present.
    sort_order : `bool`, optional (default: `True`)
        For continuous annotations used as color parameter, plot data points
        with higher values on top of others.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    components : str or list of str, optional (default: '1,2')
         String of the form '1,2' or ['1,2', '2,3'].
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object.

    Returns
    -------
    If `show==False`, a list of `matplotlib.Axis` objects. Every second element
    corresponds to the 'right margin' drawing area for color bars and legends.
    """
    if layout is None: layout = str(adata.uns['draw_graph']['params']['layout'])
    basis = 'draw_graph_' + layout
    if 'X_' + basis not in adata.obsm_keys():
        raise ValueError('Did not find {} in adata.obs. Did you compute layout {}?'
                         .format('draw_graph_' + layout, layout))
    axs = scatter(
        adata,
        basis=basis,
        color=color,
        use_raw=use_raw,
        sort_order=sort_order,
        alpha=alpha,
        groups=groups,
        components=components,
        projection='2d',
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
        legend_fontweight=legend_fontweight,
        color_map=color_map,
        palette=palette,
        right_margin=right_margin,
        size=size,
        title=title,
        show=False,
        save=False,
        ax=ax)
    if edges:
        for ax in axs:
            g = nx.Graph(adata.uns['neighbors']['connectivities'])
            edge_collection = nx.draw_networkx_edges(
                g, adata.obsm['X_' + basis],
                ax=ax, width=edges_width, edge_color=edges_color)
            edge_collection.set_zorder(-2)
    utils.savefig_or_show('scatter' if basis is None else basis, show=show, save=save)
    if show == False: return axs


def tsne(
        adata,
        color=None,
        use_raw=True,
        sort_order=True,
        alpha=None,
        groups=None,
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None, ax=None):
    """Scatter plot in tSNE basis.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    use_raw : `bool`, optional (default: `True`)
        Use `raw` attribute of `adata` if present.
    sort_order : `bool`, optional (default: `True`)
        For continuous annotations used as color parameter, plot data points
        with higher values on top of others.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object.

    Returns
    -------
    If `show==False`, a list of `matplotlib.Axis` objects. Every second element
    corresponds to the 'right margin' drawing area for color bars and legends.
    """
    axs = scatter(
        adata,
        basis='tsne',
        color=color,
        use_raw=use_raw,
        sort_order=sort_order,
        alpha=alpha,
        groups=groups,
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
        legend_fontweight=legend_fontweight,
        color_map=color_map,
        palette=palette,
        right_margin=right_margin,
        size=size,
        title=title,
        show=show,
        save=save,
        ax=ax)
    if show == False: return axs


def umap(
        adata,
        color=None,
        use_raw=True,
        sort_order=True,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None, ax=None):
    """Scatter plot in UMAP basis.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    use_raw : `bool`, optional (default: `True`)
        Use `raw` attribute of `adata` if present.
    sort_order : `bool`, optional (default: `True`)
        For continuous annotations used as color parameter, plot data points
        with higher values on top of others.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    components : str or list of str, optional (default: '1,2')
         String of the form '1,2' or ['1,2', '2,3'].
    projection : {'2d', '3d'}, optional (default: '2d')
         Projection of plot.
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object.

    Returns
    -------
    If `show==False`, a list of `matplotlib.Axis` objects. Every second element
    corresponds to the 'right margin' drawing area for color bars and legends.
    """
    axs = scatter(
        adata,
        basis='umap',
        color=color,
        use_raw=use_raw,
        sort_order=sort_order,
        alpha=alpha,
        groups=groups,
        components=components,
        projection=projection,
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
        legend_fontweight=legend_fontweight,
        color_map=color_map,
        palette=palette,
        right_margin=right_margin,
        size=size,
        title=title,
        show=show,
        save=save,
        ax=ax)
    if show == False: return axs


# ------------------------------------------------------------------------------
# Subgroup identification and ordering - clustering, pseudotime, branching
# and tree inference tools
# ------------------------------------------------------------------------------


def aga(
        adata,
        basis='tsne',
        color=None,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='on data',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        size=None,
        title=None,
        right_margin=None,
        left_margin=0.05,
        show=None,
        save=None,
        title_graph=None,
        groups_graph=None,
        color_graph=None,
        **aga_graph_params):
    """Summary figure for approximate graph abstraction.

    Consists in a scatter plot and the abstracted graph. See
    :func:`~sanpy.api.pl.aga_scatter` and :func:`~scanpy.api.pl.aga_graph` for
    most of the parameters.

    See :func:`~scanpy.api.pl.aga_path` for visualizing gene changes along paths
    through the abstracted graph.

    Additional parameters are as follows.

    Parameters
    ----------
    title : `str` or `None`, optional (default: `None`)
        Title for the scatter panel, or, if `title_graph is None`, title for the
        whole figure.
    title_graph : `str` or `None`, optional (default: `None`)
        Separate title for the abstracted graph.
    """
    axs, _, _, _ = utils.setup_axes(colors=[0, 1],
                                    right_margin=right_margin)  # dummy colors
    # set a common title for the figure
    suptitle = None
    if title is not None and title_graph is None:
        suptitle = title
        title = ''
        title_graph = ''
    elif title_graph is None:
        title_graph = 'abstracted graph'
    aga_scatter(adata,
                basis=basis,
                color=color,
                alpha=alpha,
                groups=groups,
                components=components,
                projection=projection,
                legend_loc=legend_loc,
                legend_fontsize=legend_fontsize,
                legend_fontweight=legend_fontweight,
                color_map=color_map,
                palette=palette,
                right_margin=None,
                size=size,
                title=title,
                ax=axs[0],
                show=False,
                save=False)
    aga_graph(adata, ax=axs[1], show=False, save=False, title=title_graph,
              groups=groups_graph, color=color_graph, **aga_graph_params)
    if suptitle is not None: pl.suptitle(suptitle)
    utils.savefig_or_show('aga', show=show, save=save)
    if show == False: return axs


def aga_scatter(
        adata,
        basis='tsne',
        color=None,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        size=None,
        title=None,
        right_margin=None,
        show=None,
        save=None,
        ax=None):
    """Scatter plot of aga groups.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object.

    Returns
    -------
    If `show==False`, a list of `matplotlib.Axis` objects. Every second element
    corresponds to the 'right margin' drawing area for color bars and legends.
    """
    if color is None:
        color = [adata.uns['aga_groups_key']]
    if not isinstance(color, list): color = [color]
    kwds = {}
    if 'draw_graph' in basis:
        scatter_func = draw_graph
        kwds['edges'] = True
    else:
        scatter_func = scatter
        kwds['basis'] = basis
    axs = scatter_func(
        adata,
        color=color,
        alpha=alpha,
        groups=groups,
        components=components,
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
        legend_fontweight=legend_fontweight,
        color_map=color_map,
        palette=palette,
        right_margin=right_margin,
        size=size,
        title=title,
        ax=ax,
        show=False,
        **kwds)
    utils.savefig_or_show('aga_' + basis, show=show, save=save)
    if show == False: return axs


def aga_graph(
        adata,
        solid_edges='aga_adjacency_full_confidence',
        dashed_edges=None,
        layout=None,
        root=0,
        groups=None,
        color=None,
        threshold_solid=None,
        threshold_dashed=1e-6,
        fontsize=None,
        node_size_scale=1,
        node_size_power=0.5,
        edge_width_scale=1,
        min_edge_width=None,
        max_edge_width=None,
        title='abstracted graph',
        left_margin=0.01,
        random_state=0,
        pos=None,
        cmap=None,
        frameon=True,
        rootlevel=None,
        return_pos=False,
        export_to_gexf=False,
        show=None,
        save=None,
        ax=None):
    """Plot the abstracted graph.

    This uses igraph's layout algorithms for most layouts [Csardi06]_.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    solid_edges : `str`, optional (default: 'aga_adjacency_tree_confidence')
        Key for `adata.uns` that specifies the matrix that stores the edges
        to be drawn solid black.
    dashed_edges : `str` or `None`, optional (default: 'aga_adjacency_full_confidence')
        Key for `adata.uns` that specifies the matrix that stores the edges
        to be drawn dashed grey. If `None`, no dashed edges are drawn.
    layout : {'fr', 'rt', 'rt_circular', 'eq_tree', ...}, optional (default: 'fr')
        Plotting layout. 'fr' stands for Fruchterman-Reingold, 'rt' stands for
        Reingold Tilford. 'eq_tree' stands for 'eqally spaced tree'. All but
        'eq_tree' use the igraph layout function. All other igraph layouts are
        also permitted. See also parameter `pos`.
    random_state : `int` or `None`, optional (default: 0)
        For layouts with random initialization like 'fr', change this to use
        different intial states for the optimization. If `None`, the initial
        state is not reproducible.
    root : int, str or list of int, optional (default: 0)
        If choosing a tree layout, this is the index of the root node or root
        nodes. If this is a non-empty vector then the supplied node IDs are used
        as the roots of the trees (or a single tree if the graph is
        connected. If this is `None` or an empty list, the root vertices are
        automatically calculated based on topological sorting.
    groups : `str`, `list`, `dict`
        The node (groups) labels.
    color : color string or iterable, {'degree_dashed', 'degree_solid'}, optional (default: None)
        The node colors.  Besides cluster colors, lists and uniform colors this
        also acceppts {'degree_dashed', 'degree_solid'} which are plotted using
        continuous color map.
    threshold_solid : `float` or `None`, optional (default: `None`)
        Do not draw edges for weights below this threshold. Set to `None` if you
        want all edges.
    threshold_dashed : `float` or `None`, optional (default: 1e-6)
        Do not draw edges for weights below this threshold. Set to `None` if you
        want all edges.
    fontsize : int (default: None)
        Font size for node labels.
    node_size_scale : float (default: 1.0)
        Increase or decrease the size of the nodes.
    node_size_power : float (default: 0.5)
        The power with which groups sizes influence the radius of the nodes.
    edge_width_scale : `float`, optional (default: 1.5)
        Edge with scale in units of `rcParams['lines.linewidth']`.
    min_edge_width : `float`, optional (default: `None`)
        Min width of solid edges.
    max_edge_width : `float`, optional (default: `None`)
        Max width of solid and dashed edges.
    pos : array-like, filename of `.gdf` file,  optional (default: `None`)
        Two-column array/list storing the x and y coordinates for drawing.
        Otherwise, path to a `.gdf` file that has been exported from Gephi or
        a similar graph visualization software.
    export_to_gexf : `bool`, optional (default: `None`)
        Export to gexf format to be read by graph visualization programs such as
        Gephi.
    return_pos : `bool`, optional (default: `False`)
        Return the positions.
    title : `str`, optional (default: `None`)
         Provide title for panels either as `['title1', 'title2', ...]` or
         `'title1,title2,...'`.
    frameon : `bool`, optional (default: `True`)
         Draw a frame around the abstracted graph.
    show : `bool`, optional (default: `None`)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : `matplotlib.Axes`
         A matplotlib axes object.

    Returns
    -------
    If `show==False`, a list of `matplotlib.Axis` objects. Every second element
    corresponds to the 'right margin' drawing area for color bars and legends.

    If `return_pos` is `True`, in addition, the positions of the nodes.
    """

    import matplotlib as mpl
    from distutils.version import LooseVersion
    if mpl.__version__ > LooseVersion('2.0.0'):
        logg.warn('Currently, `aga_graph` sometimes crashes with matplotlib version > 2.0, you have {}.\n'
                  'Run `pip install matplotlib==2.0` if this hits you.'
                  .format(mpl.__version__))

    # colors is a list that contains no lists
    if isinstance(color, list) and True not in [isinstance(c, list) for c in color]: color = [color]
    if color is None or isinstance(color, str): color = [color]

    # groups is a list that contains no lists
    if isinstance(groups, list) and True not in [isinstance(g, list) for g in groups]: groups = [groups]
    if groups is None or isinstance(groups, dict) or isinstance(groups, str): groups = [groups]

    if title is None or isinstance(title, str): title = [title for name in groups]

    if ax is None:
        axs, _, _, _ = utils.setup_axes(colors=color)
    else:
        axs = ax
    if len(color) == 1 and not isinstance(axs, list): axs = [axs]

    for icolor, c in enumerate(color):
        pos = _aga_graph(
            adata,
            axs[icolor],
            solid_edges=solid_edges,
            dashed_edges=dashed_edges,
            threshold_solid=threshold_solid,
            threshold_dashed=threshold_dashed,
            layout=layout,
            root=root,
            rootlevel=rootlevel,
            color=c,
            groups=groups[icolor],
            fontsize=fontsize,
            node_size_scale=node_size_scale,
            node_size_power=node_size_power,
            edge_width_scale=edge_width_scale,
            min_edge_width=min_edge_width,
            max_edge_width=max_edge_width,
            frameon=frameon,
            cmap=cmap,
            title=title[icolor],
            random_state=0,
            export_to_gexf=export_to_gexf,
            pos=pos)
    utils.savefig_or_show('aga_graph', show=show, save=save)
    if len(color) == 1 and isinstance(axs, list): axs = axs[0]
    if return_pos:
        return (axs, pos) if show == False else pos
    else:
        return axs if show == False else None


def _aga_graph(
        adata,
        ax,
        solid_edges=None,
        dashed_edges=None,
        threshold_solid=None,
        threshold_dashed=1e-6,
        root=0,
        rootlevel=None,
        color=None,
        groups=None,
        fontsize=None,
        node_size_scale=1,
        node_size_power=0.5,
        edge_width_scale=1,
        title=None,
        layout=None,
        pos=None,
        cmap=None,
        frameon=True,
        min_edge_width=None,
        max_edge_width=None,
        export_to_gexf=False,
        random_state=0):
    node_labels = groups
    if (node_labels is not None
        and isinstance(node_labels, str)
        and node_labels != adata.uns['aga_groups_key']):
        raise ValueError('Provide a list of group labels for the AGA groups {}, not {}.'
                         .format(adata.uns['aga_groups_key'], node_labels))
    groups_key = adata.uns['aga_groups_key']
    if node_labels is None:
        node_labels = adata.obs[groups_key].cat.categories

    if color is None and groups_key is not None:
        if (groups_key + '_colors' not in adata.uns
            or len(adata.obs[groups_key].cat.categories)
               != len(adata.uns[groups_key + '_colors'])):
            utils.add_colors_for_categorical_sample_annotation(adata, groups_key)
        color = adata.uns[groups_key + '_colors']
        for iname, name in enumerate(adata.obs[groups_key].cat.categories):
            if name in settings.categories_to_ignore: color[iname] = 'grey'

    if isinstance(root, str):
        if root in node_labels:
            root = list(node_labels).index(root)
        else:
            raise ValueError(
                'If `root` is a string, it needs to be one of {} not \'{}\'.'
                .format(node_labels.tolist(), root))
    if isinstance(root, list) and root[0] in node_labels:
        root = [list(node_labels).index(r) for r in root]

    # define the objects
    adjacency_solid = adata.uns[solid_edges].copy()
    if threshold_solid is not None:
        adjacency_solid[adjacency_solid < threshold_solid] = 0
    nx_g_solid = nx.Graph(adjacency_solid)
    if dashed_edges is not None:
        adjacency_dashed = adata.uns[dashed_edges].copy()
        if threshold_dashed is not None:
            adjacency_dashed[adjacency_dashed < threshold_dashed] = 0
        nx_g_dashed = nx.Graph(adjacency_dashed)

    # degree of the graph for coloring
    if isinstance(color, str) and color.startswith('degree'):
        # see also tools.aga.aga_degrees
        if color == 'degree_dashed':
            color = [d for _, d in nx_g_dashed.degree(weight='weight')]
        elif color == 'degree_solid':
            color = [d for _, d in nx_g_solid.degree(weight='weight')]
        else:
            raise ValueError('`degree` either "degree_dashed" or "degree_solid".')
        color = (np.array(color) - np.min(color)) / (np.max(color) - np.min(color))

    # plot numeric colors
    colorbar = False
    if isinstance(color, (list, np.ndarray)) and not isinstance(color[0], (str, dict)):
        import matplotlib
        norm = matplotlib.colors.Normalize()
        color = norm(color)
        if cmap is None: cmap = rcParams['image.cmap']
        cmap = matplotlib.cm.get_cmap(cmap)
        color = [cmap(c) for c in color]
        colorbar = True

    if len(color) < len(node_labels):
        print(node_labels, color)
        raise ValueError('`color` list need to be at least as long as `node_labels` list.')

    # node positions from adjacency_solid
    if pos is None:
        if layout is None:
            layout = 'fr'
        # igraph layouts
        if layout != 'eq_tree':
            from ... import utils as sc_utils
            adj_solid_weights = adjacency_solid
            g = sc_utils.get_igraph_from_adjacency(adj_solid_weights)
            if 'rt' in layout:
                pos_list = g.layout(
                    layout, root=root if isinstance(root, list) else [root],
                    rootlevel=rootlevel).coords
            elif layout == 'circle':
                pos_list = g.layout(layout).coords
            else:
                np.random.seed(random_state)
                init_coords = np.random.random((adjacency_solid.shape[0], 2)).tolist()
                pos_list = g.layout(layout, seed=init_coords, weights='weight').coords
            pos = {n: [p[0], -p[1]] for n, p in enumerate(pos_list)}
        # equally-spaced tree
        else:
            pos = utils.hierarchy_pos(nx_g_solid, root)
            if len(pos) < adjacency_solid.shape[0]:
                raise ValueError('This is a forest and not a single tree. '
                                 'Try another `layout`, e.g., {\'fr\'}.')
        pos_array = np.array([pos[n] for count, n in enumerate(nx_g_solid)])
    else:
        if isinstance(pos, str):
            if not pos.endswith('.gdf'):
                raise ValueError('Currently only supporting reading positions from .gdf files.'
                                 'Consider generating them using, for instance, Gephi.')
            s = ''  # read the node definition from the file
            with open(pos) as f:
                f.readline()
                for line in f:
                    if line.startswith('edgedef>'):
                        break
                    s += line
            from io import StringIO
            df = pd.read_csv(StringIO(s), header=-1)
            pos = df[[4, 5]].values
        pos_array = pos
        # convert to dictionary
        pos = {n: [p[0], p[1]] for n, p in enumerate(pos)}

    if len(pos) == 1: pos[0] = (0.5, 0.5)

    # edge widths
    base_edge_width = edge_width_scale * rcParams['lines.linewidth']

    # draw dashed edges
    if dashed_edges is not None:
        widths = [x[-1]['weight'] for x in nx_g_dashed.edges(data=True)]
        widths = base_edge_width * np.array(widths)
        if max_edge_width is not None:
            widths = np.clip(widths, None, max_edge_width)
        nx.draw_networkx_edges(nx_g_dashed, pos, ax=ax, width=widths, edge_color='grey',
                               style='dashed', alpha=0.5)

    # draw solid edges
    widths = [x[-1]['weight'] for x in nx_g_solid.edges(data=True)]
    widths = base_edge_width * np.array(widths)
    if min_edge_width is not None or max_edge_width is not None:
        widths = np.clip(widths, min_edge_width, max_edge_width)
    nx.draw_networkx_edges(nx_g_solid, pos, ax=ax, width=widths, edge_color='black')

    if export_to_gexf:
        for count, n in enumerate(nx_g_dashed.nodes()):
            nx_g_dashed.node[count]['label'] = node_labels[count]
            nx_g_dashed.node[count]['color'] = color[count]
            nx_g_dashed.node[count]['viz'] = {
                'position': {'x': 1000*pos[count][0],
                             'y': 1000*pos[count][1],
                             'z': 0}}
        logg.msg('exporting to {}'.format(settings.writedir + 'aga_graph.gexf'), v=1)
        nx.write_gexf(nx_g_dashed, settings.writedir + 'aga_graph.gexf')

    # deal with empty graph
    # ax.plot(pos_array[:, 0], pos_array[:, 1], '.', c='white')

    # draw the nodes (pie charts)
    trans = ax.transData.transform
    bbox = ax.get_position().get_points()
    ax_x_min = bbox[0, 0]
    ax_x_max = bbox[1, 0]
    ax_y_min = bbox[0, 1]
    ax_y_max = bbox[1, 1]
    ax_len_x = ax_x_max - ax_x_min
    ax_len_y = ax_y_max - ax_y_min
    # print([ax_x_min, ax_x_max, ax_y_min, ax_y_max])
    # print([ax_len_x, ax_len_y])
    trans2 = ax.transAxes.inverted().transform
    ax.set_frame_on(frameon)
    ax.set_xticks([])
    ax.set_yticks([])
    if (groups_key is not None and groups_key + '_sizes' in adata.uns):
        groups_sizes = adata.uns[groups_key + '_sizes']
    else:
        groups_sizes = np.ones(len(node_labels))
    base_scale_scatter = 2000
    base_pie_size = (base_scale_scatter / (np.sqrt(adjacency_solid.shape[0]) + 10)
                     * node_size_scale)
    median_group_size = np.median(groups_sizes)
    groups_sizes = base_pie_size * np.power(
        groups_sizes / median_group_size, node_size_power)
    # usual scatter plot
    if is_color_like(color[0]):
        ax.scatter(pos_array[:, 0], pos_array[:, 1],
                   c=color, edgecolors='face', s=groups_sizes)
        for count, group in enumerate(node_labels):
            ax.text(pos_array[count, 0], pos_array[count, 1], group,
                verticalalignment='center',
                horizontalalignment='center', size=fontsize)
    # else pie chart plot
    else:
        force_labels_to_front = True  # TODO: solve this differently!
        for count, n in enumerate(nx_g_solid.nodes()):
            pie_size = groups_sizes[count] / base_scale_scatter
            xx, yy = trans(pos[n])     # data coordinates
            xa, ya = trans2((xx, yy))  # axis coordinates
            xa = ax_x_min + (xa - pie_size/2) * ax_len_x
            ya = ax_y_min + (ya - pie_size/2) * ax_len_y
            # clip, the fruchterman layout sometimes places below figure
            if ya < 0: ya = 0
            if xa < 0: xa = 0
            a = pl.axes([xa, ya, pie_size * ax_len_x, pie_size * ax_len_y])
            if not isinstance(color[count], dict):
                raise ValueError('{} is neither a dict of valid matplotlib colors '
                                 'nor a valid matplotlib color.'.format(color[count]))
            color_single = color[count].keys()
            fracs = [color[count][c] for c in color_single]
            if sum(fracs) < 1:
                color_single = list(color_single)
                color_single.append('grey')
                fracs.append(1-sum(fracs))
            a.pie(fracs, colors=color_single)
            if not force_labels_to_front and node_labels is not None:
                a.text(0.5, 0.5, node_labels[count],
                       verticalalignment='center',
                       horizontalalignment='center',
                       transform=a.transAxes,
                       size=fontsize)
        # TODO: this is a terrible hack, but if we use the solution above (`not
        # force_labels_to_front`), labels get hidden behind pies
        if force_labels_to_front and node_labels is not None:
            for count, n in enumerate(nx_g_solid.nodes()):
                pie_size = groups_sizes[count] / base_scale_scatter
                # all copy and paste from above
                xx, yy = trans(pos[n])     # data coordinates
                xa, ya = trans2((xx, yy))  # axis coordinates
                # make sure a new axis is created
                xa = ax_x_min + (xa - pie_size/2.0000001) * ax_len_x
                ya = ax_y_min + (ya - pie_size/2.0000001) * ax_len_y
                # clip, the fruchterman layout sometimes places below figure
                if ya < 0: ya = 0
                if xa < 0: xa = 0
                a = pl.axes([xa, ya, pie_size * ax_len_x, pie_size * ax_len_y])
                a.set_frame_on(False)
                a.set_xticks([])
                a.set_yticks([])
                a.text(0.5, 0.5, node_labels[count],
                       verticalalignment='center',
                       horizontalalignment='center',
                       transform=a.transAxes, size=fontsize)
    if title is not None: ax.set_title(title)
    if colorbar:
        ax1 = pl.axes([0.95, 0.1, 0.03, 0.7])
        cb = matplotlib.colorbar.ColorbarBase(ax1, cmap=cmap,
                                              norm=norm)
    return pos_array


def aga_path(
        adata,
        nodes,
        keys,
        annotations=['dpt_pseudotime'],
        color_map=None,
        color_maps_annotations={'dpt_pseudotime': 'Greys'},
        palette_groups=None,
        n_avg=1,
        groups_key=None,
        xlim=[None, None],
        title=None,
        left_margin=None,
        ytick_fontsize=None,
        title_fontsize=None,
        show_node_names=True,
        show_yticks=True,
        show_colorbar=True,
        legend_fontsize=None,
        legend_fontweight=None,
        normalize_to_zero_one=False,
        as_heatmap=True,
        return_data=False,
        show=None,
        save=None,
        ax=None):
    """Gene expression and annotation changes along paths in the abstracted graph.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        An annotated data matrix.
    nodes : list of group names or their category indices
        A path through nodes of the abstracted graph, that is, names or indices
        (within `.categories`) of groups that have been used to run AGA.
    keys : list of str
        Either variables in `adata.var_names` or annotations in
        `adata.obs`. They are plotted using `color_map`.
    annotations : list of annotations, optional (default: ['dpt_pseudotime'])
        Plot these keys with `color_maps_annotations`. Need to be keys for
        `adata.obs`.
    color_map : color map for plotting keys or `None`, optional (default: `None`)
        Matplotlib colormap.
    color_maps_annotations : dict storing color maps or `None`, optional (default: {'dpt_pseudotime': 'Greys'})
        Color maps for plotting the annotations. Keys of the dictionary must
        appear in `annotations`.
    palette_groups : list of colors or `None`, optional (default: `None`)
        Ususally, use the same `sc.pl.palettes...` as used for coloring the
        abstracted graph.
    n_avg : `int`, optional (default: 1)
        Number of data points to include in computation of running average.
    groups_key : `str`, optional (default: `None`)
        Key of the grouping used to run AGA. If `None`, defaults to
        `adata.uns['aga_groups_key']`.
    as_heatmap : `bool`, optional (default: `True`)
        Plot the timeseries as heatmap. If not plotting as heatmap,
        `annotations` have no effect.
    show_node_names : `bool`, optional (default: `True`)
        Plot the node names on the nodes bar.
    show_colorbar : `bool`, optional (default: `True`)
        Show the colorbar.
    show_yticks : `bool`, optional (default: `True`)
        Show the y ticks.
    normalize_to_zero_one : `bool`, optional (default: `True`)
        Shift and scale the running average to [0, 1] per gene.
    return_data : `bool`, optional (default: `False`)
        Return the timeseries data in addition to the axes if `True`.
    show : `bool`, optional (default: `None`)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : `matplotlib.Axes`
         A matplotlib axes object.

    Returns
    -------
    A `matplotlib.Axes`, if `ax` is `None`, else `None`. If `return_data`,
    return the timeseries data in addition to an axes.
    """
    ax_was_none = ax is None

    if groups_key is None:
        if 'aga_groups_key' not in adata.uns:
            raise KeyError(
                'Pass the key of the grouping with which you ran AGA, '
                'using the parameter `groups_key`.')
        groups_key = adata.uns['aga_groups_key']
    groups_names = adata.obs[groups_key].cat.categories

    if palette_groups is None:
        utils.add_colors_for_categorical_sample_annotation(adata, groups_key)
        palette_groups = adata.uns[groups_key + '_colors']

    def moving_average(a):
        return sc_utils.moving_average(a, n_avg)

    ax = pl.gca() if ax is None else ax
    from matplotlib import transforms
    trans = transforms.blended_transform_factory(
        ax.transData, ax.transAxes)
    X = []
    x_tick_locs = [0]
    x_tick_labels = []
    groups = []
    anno_dict = {anno: [] for anno in annotations}
    if isinstance(nodes[0], str):
        nodes_ints = []
        groups_names_set = set(groups_names)
        for node in nodes:
            if node not in groups_names_set:
                raise ValueError(
                    'Each node/group needs to be one of {} (`groups_key`=\'{}\') not \'{}\'.'
                    .format(groups_names.tolist(), groups_key, node))
            nodes_ints.append(groups_names.get_loc(node))
        nodes_strs = nodes
    else:
        nodes_ints = nodes
        nodes_strs = [groups_names[node] for node in nodes]
    for ikey, key in enumerate(keys):
        x = []
        for igroup, group in enumerate(nodes_ints):
            idcs = np.arange(adata.n_obs)[
                adata.obs[groups_key].values == nodes_strs[igroup]]
            if len(idcs) == 0:
                raise ValueError(
                    'Did not find data points that match '
                    '`adata.obs[{}].values == str({})`.'
                    'Check whether adata.obs[{}] actually contains what you expect.'
                    .format(groups_key, group, groups_key))
            idcs_group = np.argsort(adata.obs['dpt_pseudotime'].values[
                adata.obs[groups_key].values == nodes_strs[igroup]])
            idcs = idcs[idcs_group]
            if key in adata.obs_keys(): x += list(adata.obs[key].values[idcs])
            else: x += list(adata[:, key].X[idcs])
            if ikey == 0:
                groups += [group for i in range(len(idcs))]
                x_tick_locs.append(len(x))
                for anno in annotations:
                    series = adata.obs[anno]
                    if is_categorical_dtype(series): series = series.cat.codes
                    anno_dict[anno] += list(series.values[idcs])
        if n_avg > 1:
            old_len_x = len(x)
            x = moving_average(x)
            if ikey == 0:
                for key in annotations:
                    if not isinstance(anno_dict[key][0], str):
                        anno_dict[key] = moving_average(anno_dict[key])
        if normalize_to_zero_one:
            x -= np.min(x)
            x /= np.max(x)
        X.append(x)
        if not as_heatmap:
            ax.plot(x[xlim[0]:xlim[1]], label=key)
        if ikey == 0:
            for igroup, group in enumerate(nodes):
                if len(groups_names) > 0 and group not in groups_names:
                    label = groups_names[group]
                else:
                    label = group
                x_tick_labels.append(label)
    X = np.array(X)
    if as_heatmap:
        img = ax.imshow(X, aspect='auto', interpolation='nearest',
                        cmap=color_map)
        if show_yticks:
            ax.set_yticks(range(len(X)))
            ax.set_yticklabels(keys, fontsize=ytick_fontsize)
        else:
            ax.set_yticks([])
        ax.set_frame_on(False)
        ax.set_xticks([])
        ax.tick_params(axis='both', which='both', length=0)
        ax.grid(False)
        if show_colorbar:
            pl.colorbar(img, ax=ax)
        left_margin = 0.2 if left_margin is None else left_margin
        pl.subplots_adjust(left=left_margin)
    else:
        left_margin = 0.4 if left_margin is None else left_margin
        if len(keys) > 1:
            pl.legend(frameon=False, loc='center left',
                      bbox_to_anchor=(-left_margin, 0.5),
                      fontsize=legend_fontsize)
    xlabel = groups_key
    if not as_heatmap:
        ax.set_xlabel(xlabel)
        pl.yticks([])
        if len(keys) == 1: pl.ylabel(keys[0] + ' (a.u.)')
    else:
        import matplotlib.colors
        # groups bar
        ax_bounds = ax.get_position().bounds
        groups_axis = pl.axes([ax_bounds[0],
                               ax_bounds[1],
                               ax_bounds[2],
                               - ax_bounds[3] / len(keys)])
        groups = np.array(groups)[None, :]
        groups_axis.imshow(groups, aspect='auto',
                           interpolation="nearest",
                           cmap=matplotlib.colors.ListedColormap(
                               # the following line doesn't work because of normalization
                               # adata.uns['aga_groups_colors'])
                               palette_groups[np.min(groups).astype(int):],
                               N=np.max(groups)+1-np.min(groups)))
        if show_yticks:
            groups_axis.set_yticklabels(['', xlabel, ''], fontsize=ytick_fontsize)
        else:
            groups_axis.set_yticks([])
        groups_axis.set_frame_on(False)
        if show_node_names:
            ypos = (groups_axis.get_ylim()[1] + groups_axis.get_ylim()[0])/2
            x_tick_locs = sc_utils.moving_average(x_tick_locs, n=2)
            for ilabel, label in enumerate(x_tick_labels):
                groups_axis.text(x_tick_locs[ilabel], ypos, x_tick_labels[ilabel],
                                 fontdict={'horizontalalignment': 'center',
                                           'verticalalignment': 'center'})
        groups_axis.set_xticks([])
        groups_axis.grid(False)
        groups_axis.tick_params(axis='both', which='both', length=0)
        # further annotations
        y_shift = ax_bounds[3] / len(keys)
        for ianno, anno in enumerate(annotations):
            if ianno > 0: y_shift = ax_bounds[3] / len(keys) / 2
            anno_axis = pl.axes([ax_bounds[0],
                                 ax_bounds[1] - (ianno+1) * y_shift,
                                 ax_bounds[2],
                                 - (ianno+1) * y_shift])
            arr = np.array(anno_dict[anno])[None, :]
            if anno not in color_maps_annotations:
                color_map_anno = ('Vega10' if is_categorical_dtype(adata.obs[anno])
                                  else 'Greys')
            else:
                color_map_anno = color_maps_annotations[anno]
            img = anno_axis.imshow(arr, aspect='auto',
                                   interpolation='nearest',
                                   cmap=color_map_anno)
            if show_yticks:
                anno_axis.set_yticklabels(['', anno, ''],
                                          fontsize=ytick_fontsize)
                anno_axis.tick_params(axis='both', which='both', length=0)
            else:
                anno_axis.set_yticks([])
            anno_axis.set_frame_on(False)
            anno_axis.set_xticks([])
            anno_axis.grid(False)
    if title is not None: ax.set_title(title, fontsize=title_fontsize)
    if show is None and not ax_was_none: show = False
    else: show = settings.autoshow if show is None else show
    utils.savefig_or_show('aga_path', show=show, save=save)
    if return_data:
        df = pd.DataFrame(data=X.T, columns=keys)
        df['groups'] = moving_average(groups)  # groups is without moving average, yet
        df['distance'] = anno_dict['dpt_pseudotime'].T
        return ax, df if ax_was_none and show == False else df
    else:
        return ax if ax_was_none and show == False else None


def aga_connectivity(
        adata,
        connectivity_type='scaled',
        color_map=None,
        show=None,
        save=None):
    """Connectivity of aga groups.
    """
    if connectivity_type == 'scaled':
        connectivity = adata.uns['aga_connectivity']
    elif connectivity_type == 'distance':
        connectivity = adata.uns['aga_distances']
    elif connectivity_type == 'absolute':
        connectivity = adata.uns['aga_connectivity_absolute']
    else:
        raise ValueError('Unkown connectivity_type {}.'.format(connectivity_type))
    adjacency = adata.uns['aga_adjacency']
    matrix(connectivity, color_map=color_map, show=False)
    for i in range(adjacency.shape[0]):
        neighbors = adjacency[i].nonzero()[1]
        pl.scatter([i for j in neighbors], neighbors, color='green')
    utils.savefig_or_show('aga_connectivity', show=show, save=save)
    # as a stripplot
    if False:
        pl.figure()
        for i, ds in enumerate(connectivity):
            ds = np.log1p(ds)
            x = [i for j, d in enumerate(ds) if i != j]
            y = [d for j, d in enumerate(ds) if i != j]
            pl.scatter(x, y, color='gray')
            neighbors = adjacency[i]
            pl.scatter([i for j in neighbors],
                       ds[neighbors], color='green')
        pl.show()


def dpt(
        adata,
        basis='diffmap',
        color=None,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None):
    """Plot results of DPT analysis.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    basis : {`'diffmap'`, `'pca'`, `'tsne'`, `'draw_graph_...'`}
        Choose the basis in which to plot.
    color : string or list of strings, optional (default: None)
        Observation/ cell annotation for coloring in the form "ann1,ann2,...". String
        annotation is plotted assuming categorical annotation, float and integer
        annotation is plotted assuming continuous annoation.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    components : str or list of str, optional (default: '1,2')
         String of the form '1,2' or ['1,2', '2,3'].
    projection : {'2d', '3d'}, optional (default: '2d')
         Projection of plot.
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    size : float (default: None)
         Point size.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object.
    show_tree : bool, optional (default: False)
         This shows the inferred tree. For more than a single branching, the
         result is pretty unreliable. Use tool `aga` (Approximate Graph
         Abstraction) instead.
    """
    colors = ['dpt_pseudotime']
    if len(np.unique(adata.obs['dpt_groups'].values)) > 1: colors += ['dpt_groups']
    if color is not None: colors = color
    dpt_scatter(
        adata,
        basis=basis,
        color=color,
        alpha=alpha,
        groups=groups,
        components=components,
        projection=projection,
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
        legend_fontweight=legend_fontweight,
        color_map=color_map,
        palette=palette,
        right_margin=right_margin,
        size=size,
        title=title,
        show=False,
        save=save)
    dpt_groups_pseudotime(adata, color_map=color_map, show=False, save=save)
    dpt_timeseries(adata, color_map=color_map, show=show, save=save)


def dpt_scatter(
        adata,
        basis='diffmap',
        color=None,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None):
    """Scatter plot of DPT results.

    See parameters of sc.pl.dpt().
    """

    colors = ['dpt_pseudotime']
    if len(np.unique(adata.obs['dpt_groups'].values)) > 1: colors += ['dpt_groups']
    if color is not None:
        if not isinstance(color, list): colors = color.split(',')
        else: colors = color
    if components == 'all':
        components_list = ['1,2', '1,3', '1,4', '1,5', '2,3', '2,4', '2,5', '3,4', '3,5', '4,5']
    else:
        if components is None:
            components = '1,2' if '2d' in projection else '1,2,3'
        if not isinstance(components, list): components_list = [components]
        else: components_list = components
    for components in components_list:
        axs = scatter(
            adata,
            basis=basis,
            color=colors,
            groups=groups,
            components=components,
            projection=projection,
            legend_loc=legend_loc,
            legend_fontsize=legend_fontsize,
            legend_fontweight=legend_fontweight,
            color_map=color_map,
            palette=palette,
            right_margin=right_margin,
            size=size,
            title=title,
            show=False)
        writekey = 'dpt_' + basis + '_components' + components.replace(',', '')
        utils.savefig_or_show(writekey, show=show, save=save)


def dpt_timeseries(adata, color_map=None, show=None, save=None, as_heatmap=True):
    """Heatmap of pseudotime series.

    Parameters
    ----------
    as_heatmap : bool (default: False)
        Plot the timeseries as heatmap.
    """
    if adata.n_vars > 100:
        logg.warn('Plotting more than 100 genes might take some while,'
                  'consider selecting only highly variable genes, for example.')
    # only if number of genes is not too high
    if as_heatmap:
        # plot time series as heatmap, as in Haghverdi et al. (2016), Fig. 1d
        timeseries_as_heatmap(adata.X[adata.obs['dpt_order_indices'].values],
                              var_names=adata.var_names,
                              highlightsX=adata.uns['dpt_changepoints'],
                              color_map=color_map)
    else:
        # plot time series as gene expression vs time
        timeseries(adata.X[adata.obs['dpt_order_indices'].values],
                   var_names=adata.var_names,
                   highlightsX=adata.uns['dpt_changepoints'],
                   xlim=[0, 1.3*adata.X.shape[0]])
    pl.xlabel('dpt order')
    utils.savefig_or_show('dpt_timeseries', save=save, show=show)


def dpt_groups_pseudotime(adata, color_map=None, palette=None, show=None, save=None):
    """Plot groups and pseudotime."""
    pl.figure()
    pl.subplot(211)
    timeseries_subplot(adata.obs['dpt_groups'].cat.codes,
                       time=adata.obs['dpt_order'].values,
                       color=np.asarray(adata.obs['dpt_groups']),
                       highlightsX=adata.uns['dpt_changepoints'],
                       ylabel='dpt groups',
                       yticks=(np.arange(len(adata.obs['dpt_groups'].cat.categories), dtype=int)
                                     if len(adata.obs['dpt_groups'].cat.categories) < 5 else None),
                       palette=palette)
    pl.subplot(212)
    timeseries_subplot(adata.obs['dpt_pseudotime'].values,
                       time=adata.obs['dpt_order'].values,
                       color=adata.obs['dpt_pseudotime'].values,
                       xlabel='dpt order',
                       highlightsX=adata.uns['dpt_changepoints'],
                       ylabel='pseudotime',
                       yticks=[0, 1],
                       color_map=color_map)
    utils.savefig_or_show('dpt_groups_pseudotime', save=save, show=show)


def louvain(
        adata,
        basis='tsne',
        color=None,
        alpha=None,
        groups=None,
        components=None,
        projection='2d',
        legend_loc='right margin',
        legend_fontsize=None,
        legend_fontweight=None,
        color_map=None,
        palette=None,
        right_margin=None,
        size=None,
        title=None,
        show=None,
        save=None, ax=None):
    """Plot results of Louvain clustering.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    basis : {`'diffmap'`, `'pca'`, `'tsne'`, `'draw_graph_...'`}
        Choose the basis in which to plot.
    color : string or list of strings, optional (default: None)
        Keys for observation/cell annotation either as list `["ann1", "ann2"]` or
        string `"ann1,ann2,..."`.
    groups : str, optional (default: all groups)
        Restrict to a few categories in categorical observation annotation.
    components : str or list of str, optional (default: '1,2')
         String of the form '1,2' or ['1,2', '2,3'].
    projection : {'2d', '3d'}, optional (default: '2d')
         Projection of plot.
    legend_loc : str, optional (default: 'right margin')
         Location of legend, either 'on data', 'right margin' or valid keywords
         for matplotlib.legend.
    legend_fontsize : int (default: None)
         Legend font size.
    color_map : str (default: `matplotlib.rcParams['image.cmap']`)
         String denoting matplotlib color map.
    palette : list of str (default: None)
         Colors to use for plotting groups (categorical annotation).
    right_margin : float or list of floats (default: None)
         Adjust the width of the space right of each plotting panel.
    title : str, optional (default: None)
         Provide title for panels either as `["title1", "title2", ...]` or
         `"title1,title2,..."`.
    show : bool, optional (default: None)
         Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : matplotlib.Axes
         A matplotlib axes object.
    """
    add_color = []
    if color is not None:
        add_color = color if isinstance(color, list) else color.split(',')
    color = ['louvain_groups'] + add_color
    axs = scatter(
        adata,
        basis=basis,
        color=color,
        alpha=alpha,
        groups=groups,
        components=components,
        projection=projection,
        legend_loc=legend_loc,
        legend_fontsize=legend_fontsize,
        legend_fontweight=legend_fontweight,
        color_map=color_map,
        palette=palette,
        right_margin=right_margin,
        size=size,
        title=title,
        show=False,
        save=False)
    utils.savefig_or_show('louvain_' + basis, show=show, save=save)


def rank_genes_groups(adata, groups=None, n_genes=20, fontsize=8, show=None, save=None, ext=None):
    """Plot ranking of genes.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    groups : `str` or `list` of `str`
        The groups for which to show the gene ranking.
    n_genes : `int`, optional (default: 20)
        Number of genes to show.
    fontsize : `int`, optional (default: 8)
        Fontsize for gene names.
    show : `bool`, optional (default: `None`)
        Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : `matplotlib.Axes`, optional (default: `None`)
        A `matplotlib.Axes` object.
    """
    groups_key = str(adata.uns['rank_genes_groups']['params']['groupby'])
    reference = str(adata.uns['rank_genes_groups']['params']['reference'])
    group_names = (adata.uns['rank_genes_groups']['names'].dtype.names
                   if groups is None else groups)
    # one panel for each group
    n_panels = len(group_names)
    # set up the figure
    if n_panels <= 5:
        n_panels_y = 1
        n_panels_x = n_panels
    else:
        n_panels_y = 2
        n_panels_x = int(n_panels/2+0.5)
    from matplotlib import gridspec
    fig = pl.figure(figsize=(n_panels_x * rcParams['figure.figsize'][0],
                             n_panels_y * rcParams['figure.figsize'][1]))
    left = 0.2/n_panels_x
    bottom = 0.13/n_panels_y
    gs = gridspec.GridSpec(nrows=n_panels_y,
                           ncols=n_panels_x,
                           left=left,
                           right=1-(n_panels_x-1)*left-0.01/n_panels_x,
                           bottom=bottom,
                           top=1-(n_panels_y-1)*bottom-0.1/n_panels_y,
                           wspace=0.18)

    for count, group_name in enumerate(group_names):
        pl.subplot(gs[count])
        gene_names = adata.uns['rank_genes_groups']['names'][group_name]
        scores = adata.uns['rank_genes_groups']['scores'][group_name]
        for ig, g in enumerate(gene_names[:n_genes]):
            pl.text(ig, scores[ig], gene_names[ig],
                    rotation='vertical', verticalalignment='bottom',
                    horizontalalignment='center', fontsize=fontsize)
        pl.title('{} vs. {}'.format(group_name, reference))
        if n_panels <= 5 or count >= n_panels_x: pl.xlabel('ranking')
        if count == 0 or count == n_panels_x: pl.ylabel('score')
        ymin = np.min(scores)
        ymax = np.max(scores)
        ymax += 0.3*(ymax-ymin)
        pl.ylim([ymin, ymax])
        pl.xlim(-0.9, ig+1-0.1)
    writekey = ('rank_genes_groups_'
                + str(adata.uns['rank_genes_groups']['params']['groupby']))
    utils.savefig_or_show(writekey, show=show, save=save)


def rank_genes_groups_violin(adata, groups=None, n_genes=20,
                             use_raw=None,
                             split=True,
                             scale='width',
                             strip=True, jitter=True, size=1,
                             computed_distribution=False,
                             ax=None, show=None, save=None):
    """Plot ranking of genes for all tested comparisons.

    Parameters
    ----------
    adata : :class:`~scanpy.api.AnnData`
        Annotated data matrix.
    groups : list of `str`, optional (default: `None`)
        List of group names.
    n_genes : `int`, optional (default: 20)
        Number of genes to show.
    use_raw : `bool`, optional (default: `None`)
        Use `raw` attribute of `adata` if present. Defaults to the value that
        was used in :func:`~scanpy.api.tl.rank_genes_groups`.
    split : `bool`, optional (default: `True`)
        Whether to split the violins or not.
    scale : `str` (default: 'width')
        See `seaborn.violinplot`.
    strip : `bool` (default: `True`)
        Show a strip plot on top of the violin plot.
    jitter : `int`, `float`, `bool`, optional (default: `True`)
        If set to 0, no points are drawn. See `seaborn.stripplot`.
    size : `int`, optional (default: 1)
        Size of the jitter points.
    computed_distribution : `bool`, optional (default: `False`)
        Set to `True` if you want to use the scaled and shifted distribution
        previously computed with the `compute_distribution` in
        :func:`scanpy.api.tl.rank_genes_groups`
    show : `bool`, optional (default: `None`)
        Show the plot, do not return axis.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    ax : `matplotlib.Axes`, optional (default: `None`)
        A `matplotlib.Axes` object.
    """
    from ..tools import rank_genes_groups
    groups_key = str(adata.uns['rank_genes_groups']['params']['groupby'])
    if use_raw is None:
        use_raw = bool(adata.uns['rank_genes_groups']['params']['use_raw'])
    reference = str(adata.uns['rank_genes_groups']['params']['reference'])
    groups_names = (adata.uns['rank_genes_groups']['names'].dtype.names
                    if groups is None else groups)
    if isinstance(groups_names, str): groups_names = [groups_names]
    for group_name in groups_names:
        keys = []
        gene_names = adata.uns[
            'rank_genes_groups']['names'][group_name][:n_genes]
        if computed_distribution:
            for gene_counter, gene_name in enumerate(gene_names):
                identifier = rank_genes_groups._build_identifier(
                    groups_key, group_name, gene_counter, gene_name)
                if compute_distribution and identifier not in set(adata.obs_keys()):
                    raise ValueError(
                        'You need to set `compute_distribution=True` in '
                        '`sc.tl.rank_genes_groups()`.')
                keys.append(identifier)
        else:
            keys = gene_names
        # make a "hue" option!
        df = pd.DataFrame()
        for key in keys:
            if adata.raw is not None and use_raw:
                X_col = adata.raw[:, key].X
            else:
                X_col = adata[:, key].X
            if issparse(X_col): X_col = X_col.toarray().flatten()
            df[key] = X_col
        df['hue'] = adata.obs[groups_key].astype(str).values
        if reference == 'rest':
            df['hue'][df['hue'] != group_name] = 'rest'
        else:
            df['hue'][~df['hue'].isin([group_name, reference])] = np.nan
        df['hue'] = df['hue'].astype('category')
        df_tidy = pd.melt(df, id_vars='hue', value_vars=keys)
        x = 'variable'
        y = 'value'
        hue_order = [group_name, reference]
        import seaborn as sns
        ax = sns.violinplot(x=x, y=y, data=df_tidy, inner=None,
                            hue_order=hue_order, hue='hue', split=split,
                            scale=scale, orient='vertical', ax=ax)
        if strip:
            ax = sns.stripplot(x=x, y=y, data=df_tidy,
                               hue='hue', dodge=True, hue_order=hue_order,
                               jitter=jitter, color='black', size=size, ax=ax)
        ax.set_xlabel('genes')
        ax.set_title('{} vs. {}'.format(group_name, reference))
        ax.legend_.remove()
        if computed_distribution: ax.set_ylabel('z-score w.r.t. to bulk mean')
        else: ax.set_ylabel('expression')
        ax.set_xticklabels(gene_names, rotation='vertical')
        writekey = ('rank_genes_groups_'
                    + str(adata.uns['rank_genes_groups']['params']['groupby'])
                    + '_' + group_name)
        utils.savefig_or_show(writekey, show=show, save=save)


def sim(adata, tmax_realization=None, as_heatmap=False, shuffle=False,
        show=None, save=None):
    """Plot results of simulation.

    Parameters
    ----------
    as_heatmap : bool (default: False)
        Plot the timeseries as heatmap.
    tmax_realization : int or None (default: False)
        Number of observations in one realization of the time series. The data matrix
        adata.X consists in concatenated realizations.
    shuffle : bool, optional (default: False)
        Shuffle the data.
    save : `bool` or `str`, optional (default: `None`)
        If `True` or a `str`, save the figure. A string is appended to the
        default filename. Infer the filetype if ending on \{'.pdf', '.png', '.svg'\}.
    show : bool, optional (default: None)
        Show the plot, do not return axis.
    """
    from ... import utils as sc_utils
    if tmax_realization is not None: tmax = tmax_realization
    elif 'tmax_write' in adata.uns: tmax = adata.uns['tmax_write']
    else: tmax = adata.n_obs
    n_realizations = adata.n_obs/tmax
    if not shuffle:
        if not as_heatmap:
            timeseries(adata.X,
                       var_names=adata.var_names,
                       xlim=[0, 1.25*adata.n_obs],
                       highlightsX=np.arange(tmax, n_realizations*tmax, tmax),
                       xlabel='realizations')
        else:
            # plot time series as heatmap, as in Haghverdi et al. (2016), Fig. 1d
            timeseries_as_heatmap(adata.X,
                                  var_names=adata.var_names,
                                  highlightsX=np.arange(tmax, n_realizations*tmax, tmax))
        pl.xticks(np.arange(0, n_realizations*tmax, tmax),
                  np.arange(n_realizations).astype(int) + 1)
        utils.savefig_or_show('sim', save=save, show=show)
    else:
        # shuffled data
        X = adata.X
        X, rows = sc_utils.subsample(X, seed=1)
        timeseries(X,
                   var_names=adata.var_names,
                   xlim=[0, 1.25*adata.n_obs],
                   highlightsX=np.arange(tmax, n_realizations*tmax, tmax),
                   xlabel='index (arbitrary order)')
        utils.savefig_or_show('sim_shuffled', save=save, show=show)
