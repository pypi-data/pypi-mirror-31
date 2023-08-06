"""
This is the primary module responsible for generating svg visualizations

"""
import re

from .util import dynamic_label_color, generate_interval_mapping, LabelMapping, split_intervals_into_tracks, Tag
from ..annotate.variant import FusionTranscript
from ..constants import CODON_SIZE, GIEMSA_STAIN, ORIENT, STRAND
from ..error import DrawingFitError, NotSpecifiedError
from ..interval import Interval

# draw gene level view
# draw gene box
HEX_WHITE = '#FFFFFF'
HEX_BLACK = '#000000'


def draw_legend(config, canvas, swatches, border=True):
    """
    generates an svg group object representing the legend
    """
    main_group = canvas.g(class_='legend')
    y = config.padding if border else 0
    x = config.padding if border else 0
    for swatch, label in swatches:
        svg_group = canvas.g()
        svg_group.add(canvas.rect(
            (0, 0),
            (config.legend_swatch_size, config.legend_swatch_size),
            fill=swatch,
            stroke=config.legend_swatch_stroke
        ))

        svg_group.add(canvas.text(
            label,
            insert=(config.legend_swatch_size + config.padding, config.legend_swatch_size / 2),
            fill=config.legend_font_color,
            style=config.font_style.format(text_anchor='start', font_size=config.legend_font_size),
            class_='label'
        ))
        svg_group.translate(x, y)
        main_group.add(svg_group)
        y += config.legend_swatch_size + config.padding

    width = max([len(l) for c, l in swatches]) * config.legend_font_size * config.font_width_height_ratio + \
        config.padding * (3 if border else 1) + config.legend_swatch_size

    if border:
        main_group.add(canvas.rect(
            (0, 0), (width, y), fill='none', stroke=config.legend_border_stroke,
            stroke_width=config.legend_border_stroke_width
        ))
    else:
        y -= config.padding
    setattr(main_group, 'height', y)
    setattr(main_group, 'width', width)
    setattr(main_group, 'labels', None)
    setattr(main_group, 'mapping', None)
    return main_group


def draw_exon_track(config, canvas, transcript, mapping, colors=None, x_start=None, x_end=None, translation=None):
    """
    """
    colors = {} if colors is None else colors
    main_group = canvas.g(class_='exon_track')

    y = config.track_height / 2
    exons = sorted(transcript.exons, key=lambda x: x.start)

    start = Interval.convert_ratioed_pos(mapping, exons[0].start).start if x_start is None else x_start
    end = Interval.convert_ratioed_pos(mapping, exons[-1].end).end if x_end is None else x_end

    main_group.add(
        canvas.rect(
            (start, y - config.scaffold_height / 2), (end - start + 1, config.scaffold_height),
            fill=config.scaffold_color, class_='scaffold'
        ))

    # draw the exons
    for exon in exons:
        start = Interval.convert_ratioed_pos(mapping, exon.start).start
        end = Interval.convert_ratioed_pos(mapping, exon.end).end
        pxi = Interval(start, end)
        exon_number = 'n'
        try:
            exon_number = transcript.exon_number(exon)
        except KeyError:
            pass
        group = draw_exon(
            config,
            canvas, exon, pxi.length(), config.track_height, colors.get(exon, config.exon1_color),
            label=exon_number,
            translation=translation
        )
        group.translate(pxi.start, y - config.track_height / 2)
        main_group.add(group)

    setattr(main_group, 'height', y + config.track_height / 2)
    setattr(main_group, 'width', end - start + 1)
    return main_group


def draw_transcript_with_translation(
    config, canvas, translation, labels, colors, mapping, reference_genome=None, x_start=None, x_end=None
):
    main_group = canvas.g()
    pre_transcript = translation.transcript.reference_object
    spl_tx = translation.transcript

    if x_start is None:
        x_start = Interval.convert_ratioed_pos(mapping, pre_transcript.start).start
    if x_end is None:
        x_end = Interval.convert_ratioed_pos(mapping, pre_transcript.end).end

    label_prefix = config.transcript_label_prefix
    if isinstance(pre_transcript, FusionTranscript):
        label_prefix = config.fusion_label_prefix

    # if the splicing takes up more room than the track we need to adjust for it
    y = config.splice_height

    exon_track_group = draw_exon_track(config, canvas, pre_transcript, mapping, colors, translation=translation)
    exon_track_group.translate(0, y)
    exon_track_group.add(canvas.text(
        labels.add(spl_tx, label_prefix),
        insert=(
            0 - config.padding,
            config.track_height / 2 + config.font_central_shift_ratio * config.label_font_size
        ),
        fill=config.label_color,
        style=config.font_style.format(font_size=config.label_font_size, text_anchor='end'),
        class_='label'
    ))
    exon_track_group.add(Tag('title', 'Transcript: {}'.format(pre_transcript.name if pre_transcript.name else '')))

    # draw the splicing pattern
    splice_group = canvas.g(class_='splicing')
    for p1, p2 in zip(spl_tx.splicing_pattern[::2], spl_tx.splicing_pattern[1::2]):
        a = Interval.convert_pos(mapping, p1.pos)
        b = Interval.convert_pos(mapping, p2.pos)
        polyline = [(a, y), (a + (b - a) / 2, y - config.splice_height), (b, y)]
        p = canvas.polyline(polyline, fill='none')
        p.dasharray(config.splice_stroke_dasharray)
        p.stroke(config.splice_color, width=config.splice_stroke_width)
        splice_group.add(p)

    y += config.track_height / 2

    main_group.add(splice_group)
    main_group.add(exon_track_group)
    y += config.track_height / 2

    protein_group = canvas.g(class_='protein')
    y += config.padding
    protein_group.translate(0, y)
    # translation track

    # convert the AA position to cdna position, then convert the cdna to genomic, etc
    # ==================== adding the translation track ============
    translated_genomic_regions = [
        spl_tx.convert_cdna_to_genomic(translation.start),
        spl_tx.convert_cdna_to_genomic(translation.end)
    ]
    translated_genomic_regions = [Interval(*sorted(translated_genomic_regions))]

    for p1, p2 in zip(spl_tx.splicing_pattern[::2], spl_tx.splicing_pattern[1::2]):
        try:
            spliced_out_interval = Interval(p1.pos + 1, p2.pos - 1)
            temp = []
            for region in translated_genomic_regions:
                temp.extend(region - spliced_out_interval)
            translated_genomic_regions = temp
        except AttributeError:
            pass

    s = Interval.convert_pos(mapping, translated_genomic_regions[0].start)
    t = Interval.convert_pos(mapping, translated_genomic_regions[-1].end)

    gt = canvas.g(class_='translation')
    protein_group.add(gt)
    h = config.translation_track_height

    for sec in translated_genomic_regions:
        start = Interval.convert_pos(mapping, sec.start)
        end = Interval.convert_pos(mapping, sec.end)
        gt.add(
            canvas.rect(
                (start, h / 2 - config.translation_track_height / 2), (end - start + 1, config.translation_track_height),
                fill=config.translation_scaffold_color,
                class_='scaffold'
            ))
    gt.add(canvas.text(
        config.translation_end_marker if spl_tx.get_strand() == STRAND.NEG else config.translation_start_marker,
        insert=(
            s - config.translation_marker_padding, h / 2 + config.font_central_shift_ratio * config.translation_font_size
        ),
        fill=config.label_color,
        style=config.font_style.format(font_size=config.translation_font_size, text_anchor='end'),
        class_='label'
    ))
    gt.add(canvas.text(
        config.translation_start_marker if spl_tx.get_strand() == STRAND.NEG else config.translation_end_marker,
        insert=(
            t + config.translation_marker_padding, h / 2 + config.font_central_shift_ratio * config.translation_font_size
        ),
        fill=config.label_color,
        style=config.font_style.format(font_size=config.translation_font_size, text_anchor='start'),
        class_='label'
    ))
    gt.add(Tag('title', 'translation  cdna({}_{})  c.{}_{}  p.{}_{}'.format(
        translation.start, translation.end, 1, len(translation), 1, len(translation) // CODON_SIZE)))
    py = h
    # now draw the domain tracks
    # need to convert the domain AA positions to cds positions to genomic
    for i, d in enumerate(sorted(translation.domains, key=lambda x: x.name)):
        if not re.match(config.domain_name_regex_filter, str(d.name)):
            continue
        py += config.padding
        domain_group = canvas.g(class_='domain')
        domain_group.add(canvas.rect(
            (x_start, config.domain_track_height / 2), (x_end - x_start, config.domain_scaffold_height),
            fill=config.domain_scaffold_color, class_='scaffold'
        ))
        fill = config.domain_color
        percent_match = None
        try:
            match, total = d.score_region_mapping(reference_genome)
            percent_match = int(round(match * 100 / total, 0))
            fill = config.domain_fill_gradient[percent_match % len(config.domain_fill_gradient) - 1]
        except (NotSpecifiedError, AttributeError):
            pass
        for region in d.regions:
            # convert the AA position to cdna position, then convert the cdna to genomic, etc
            s = translation.convert_aa_to_cdna(region.start)
            t = translation.convert_aa_to_cdna(region.end)
            s = Interval.convert_pos(mapping, spl_tx.convert_cdna_to_genomic(s.start))
            t = Interval.convert_pos(mapping, spl_tx.convert_cdna_to_genomic(t.end))
            if s > t:
                t, s = (s, t)
            domain_region_group = canvas.g(class_='domain_region')
            domain_region_group.add(canvas.rect((s, 0), (t - s + 1, config.domain_track_height), fill=fill, class_='region'))
            domain_region_group.add(Tag('title', 'domain {} region p.{}_{}{}'.format(
                d.name if d.name else '', region.start, region.end,
                '  matched({}%)'.format(percent_match) if percent_match is not None else '')))
            domain_group.add(domain_region_group)
        domain_group.translate(0, py)

        f = config.label_color if not config.dynamic_labels else dynamic_label_color(config.domain_color)
        label_group = None
        for patt, link in config.domain_links.items():
            if re.match(patt, d.name):
                label_group = canvas.a(link.format(d), target='_blank')
                break
        if label_group is None:
            label_group = canvas.g()
        domain_group.add(label_group)
        label_group.add(canvas.text(
            labels.add(d.name, config.domain_label_prefix),
            insert=(
                0 - config.padding,
                config.domain_track_height / 2 + config.font_central_shift_ratio * config.domain_label_font_size),
            fill=f, class_='label',
            style=config.font_style.format(font_size=config.domain_label_font_size, text_anchor='end')
        ))
        protein_group.add(domain_group)
        py += config.domain_track_height
    y += py
    main_group.add(protein_group)
    setattr(main_group, 'height', y)
    return main_group


def draw_ustranscript(
    config, canvas, pre_transcript, target_width=None, breakpoints=[], labels=LabelMapping(), colors={},
    mapping=None, reference_genome=None, masks=None
):
    """
    builds an svg group representing the transcript. Exons are drawn in a track with the splicing
    information and domains are drawn in separate tracks below

    if there are multiple splicing variants then multiple exon tracks are drawn

    Args:
        canvas (svgwrite.drawing.Drawing): the main svgwrite object used to create new svg elements
        target_width (int): the target width of the diagram
        pre_transcript (Transcript): the transcript being drawn
        exon_color (str): the color being used for the fill of the exons
        utr_color (str): the color for the fill of the UTR regions
        abrogated_splice_sites (:class:`list` of :class:`int`): list of positions to ignore as splice sites
        breakpoints (:class:`list` of :class:`Breakpoint`): the breakpoints to overlay

    Return:
        svgwrite.container.Group: the group element for the transcript diagram
                Has the added parameters of labels, height, and mapping
    """

    if pre_transcript.get_strand() not in [STRAND.POS, STRAND.NEG]:
        raise NotSpecifiedError('strand must be positive or negative to draw the pre_transcript')
    if (mapping is None and target_width is None) or (mapping is not None and target_width is not None):
        raise AttributeError('mapping and target_width arguments are required and mutually exclusive')

    if mapping is None:
        mapping = generate_interval_mapping(
            pre_transcript.exons,
            target_width,
            config.exon_intron_ratio,
            config.exon_min_width,
            min_inter_width=config.min_width
        )

    main_group = canvas.g(class_='pre_transcript')

    y = config.breakpoint_top_margin if len(breakpoints) > 0 else 0
    x_start = Interval.convert_ratioed_pos(mapping, pre_transcript.start).start
    x_end = Interval.convert_ratioed_pos(mapping, pre_transcript.end).end

    if target_width:
        x_start = 0
        x_end = target_width

    if masks is None:
        masks = []
        try:
            if len(breakpoints) == 1:
                b = breakpoints[0]
                if b.orient == ORIENT.RIGHT:
                    masks = [Interval(pre_transcript.start, b.start - 1)]
                elif b.orient == ORIENT.LEFT:
                    masks = [Interval(b.end + 1, pre_transcript.end)]
            elif len(breakpoints) == 2:
                b1, b2 = sorted(breakpoints)
                if b1.orient == ORIENT.LEFT and b2.orient == ORIENT.RIGHT:
                    masks = [Interval(b1.end + 1, b2.start - 1)]
        except AttributeError:
            pass

    label_prefix = config.transcript_label_prefix
    if isinstance(pre_transcript, FusionTranscript):
        label_prefix = config.fusion_label_prefix

    if len(pre_transcript.translations) == 0:
        y += config.splice_height
        exon_track_group = draw_exon_track(config, canvas, pre_transcript, mapping, colors)
        exon_track_group.translate(0, y)
        exon_track_group.add(canvas.text(
            labels.add(pre_transcript, label_prefix),
            insert=(0 - config.padding, config.track_height / 2 + config.font_central_shift_ratio * config.label_font_size),
            fill=config.label_color,
            style=config.font_style.format(font_size=config.label_font_size, text_anchor='end'),
            class_='label'
        ))
        exon_track_group.add(Tag('title', 'Transcript: {}'.format(pre_transcript.name if pre_transcript.name else '')))
        main_group.add(exon_track_group)
        y += config.track_height
    else:
        # draw the protein features if there are any
        for i, tl in enumerate(pre_transcript.translations):
            gp = draw_transcript_with_translation(
                config, canvas, tl, labels, colors, mapping, x_start=x_start, x_end=x_end
            )
            gp.translate(0, y)
            if i < len(pre_transcript.translations) - 1:
                y += config.inner_margin
            y += gp.height
            main_group.add(gp)

    y += config.breakpoint_bottom_margin if len(breakpoints) > 0 else 0
    # add masks
    for mask in masks:
        pixel = Interval.convert_ratioed_pos(mapping, mask.start) | Interval.convert_ratioed_pos(mapping, mask.end)
        m = canvas.rect(
            (pixel.start, 0), (pixel.length(), y),
            class_='mask', fill=config.mask_fill, opacity=config.mask_opacity, pointer_events='none'
        )
        main_group.add(m)

    # now overlay the breakpoints on top of everything
    for i, b in enumerate(breakpoints):
        pixel = Interval.convert_ratioed_pos(mapping, b.start) | Interval.convert_ratioed_pos(mapping, b.end)
        bg = draw_breakpoint(config, canvas, b, pixel.length(), y, label=labels.add(b, config.breakpoint_label_prefix))
        bg.translate(pixel.start, 0)
        main_group.add(bg)

    setattr(main_group, 'height', y)
    setattr(main_group, 'width', x_end - x_start)
    setattr(main_group, 'mapping', mapping)
    setattr(main_group, 'labels', labels)
    return main_group


def draw_genes(config, canvas, genes, target_width, breakpoints=None, colors=None, labels=None, plots=None, masks=None):
    """
    draws the genes given in order of their start position trying to minimize
    the number of tracks required to avoid overlap

    Args:
        canvas (svgwrite.drawing.Drawing): the main svgwrite object used to create new svg elements
        target_width (int): the target width of the diagram
        genes (:class:`list` of :class:`Gene`): the list of genes to draw
        breakpoints (:class:`list` of :class:`Breakpoint`): the breakpoints to overlay
        colors (:class:`dict` of :class:`Gene` and :class:`str`): dictionary of the colors assigned to each Gene as
         fill

    Return:
        svgwrite.container.Group: the group element for the diagram.
            Has the added parameters of labels, height, and mapping
    """
    # mutable default argument parameters
    breakpoints = [] if breakpoints is None else breakpoints
    colors = {} if colors is None else colors
    labels = LabelMapping() if labels is None else labels
    plots = plots if plots else []

    st = max(min([g.start for g in genes] + [b.start for b in breakpoints]) - config.gene_min_buffer, 1)
    end = max([g.end for g in genes] + [b.end for b in breakpoints]) + config.gene_min_buffer
    main_group = canvas.g(class_='genes')
    mapping = generate_interval_mapping(
        [g for g in genes],
        target_width,
        config.gene_intergenic_ratio,
        config.gene_min_width,
        start=st, end=end,
        min_inter_width=config.min_width
    )
    if masks is None:
        masks = []
        try:
            if len(breakpoints) == 1:
                b = breakpoints[0]
                if b.orient == ORIENT.RIGHT:
                    masks = [Interval(st, b.start - 1)]
                elif b.orient == ORIENT.LEFT:
                    masks = [Interval(b.end + 1, end)]
            elif len(breakpoints) == 2:
                b1, b2 = sorted(breakpoints)
                if b1.orient == ORIENT.LEFT and b2.orient == ORIENT.RIGHT:
                    masks = [Interval(b1.end, b2.start)]
        except AttributeError:
            pass

    gene_px_intervals = {}
    for i, gene in enumerate(sorted(genes, key=lambda x: x.start)):
        s = Interval.convert_ratioed_pos(mapping, gene.start)
        t = Interval.convert_ratioed_pos(mapping, gene.end)
        gene_px_intervals[Interval(s.start, t.end)] = gene
        labels.add(gene, config.gene_label_prefix)
    tracks = split_intervals_into_tracks(gene_px_intervals)

    y = config.breakpoint_top_margin

    main_group.add(
        canvas.rect(
            (0, y + config.track_height / 2 - config.scaffold_height / 2 +
                (len(tracks) - 1) * (config.track_height + config.padding)),
            (target_width, config.scaffold_height),
            fill=config.scaffold_color,
            class_='scaffold'
        ))
    tracks.reverse()
    for track in tracks:  # svg works from top down
        for genepx in track:
            # draw the gene
            gene = gene_px_intervals[genepx]
            group = draw_gene(
                config, canvas, gene, genepx.length(),
                config.track_height,
                colors.get(gene, config.gene1_color),
                labels.get_key(gene)
            )
            group.translate(genepx.start, y)
            main_group.add(group)
        y += config.track_height + config.padding

    y += config.breakpoint_bottom_margin - config.padding

    # adding the masks is the final step
    for mask in masks:
        pixel = Interval.convert_ratioed_pos(mapping, mask.start) | Interval.convert_ratioed_pos(mapping, mask.end)
        m = canvas.rect(
            (pixel.start, 0), (pixel.length(), y),
            class_='mask', fill=config.mask_fill, pointer_events='none', opacity=config.mask_opacity
        )
        main_group.add(m)

    # now overlay the breakpoints on top of everything
    for i, b in enumerate(sorted(breakpoints)):
        s = Interval.convert_ratioed_pos(mapping, b.start).start
        t = Interval.convert_ratioed_pos(mapping, b.end).end
        bg = draw_breakpoint(config, canvas, b, abs(t - s) + 1, y, label=labels.add(b, config.breakpoint_label_prefix))
        bg.translate(s, 0)
        main_group.add(bg)

    setattr(main_group, 'height', y)
    setattr(main_group, 'width', target_width)
    setattr(main_group, 'mapping', mapping)
    setattr(main_group, 'labels', labels)

    return main_group


def draw_vmarker(config, canvas, marker, width, height, label='', color=None):
    """
    Args:
        canvas (svgwrite.drawing.Drawing): the main svgwrite object used to create new svg elements
        breakpoint (Breakpoint): the breakpoint to draw
        width (int): the pixel width
        height (int): the pixel height
    Return:
        svgwrite.container.Group: the group element for the diagram
    """
    color = config.marker_color if color is None else color
    width = max([config.abs_min_width, width])
    g = canvas.g(class_='marker')
    y = config.padding + config.marker_label_font_size / 2
    t = canvas.text(
        label,
        insert=(width / 2, y + config.font_central_shift_ratio * config.marker_label_font_size),
        fill=color,
        style=config.font_style.format(text_anchor='middle', font_size=config.marker_label_font_size),
        class_='label'
    )
    y += config.marker_label_font_size / 2 + config.padding

    g.add(t)
    g.add(canvas.rect((0, y), (width, height - y), stroke=color, fill='none'))
    g.add(Tag('title', 'marker {}:{}-{} {}'.format(
        marker.reference_object, marker.start, marker.end, marker.name)))
    return g


def draw_breakpoint(config, canvas, breakpoint, width, height, label=''):
    """
    Args:
        canvas (svgwrite.drawing.Drawing): the main svgwrite object used to create new svg elements
        breakpoint (Breakpoint): the breakpoint to draw
        width (int): the pixel width
        height (int): the pixel height
    Return:
        svgwrite.container.Group: the group element for the diagram
    """
    g = canvas.g(class_='breakpoint')
    y = config.padding + config.breakpoint_label_font_size / 2
    t = canvas.text(
        label,
        insert=(width / 2, y + config.font_central_shift_ratio * config.breakpoint_label_font_size),
        fill=HEX_BLACK,
        style=config.font_style.format(text_anchor='middle', font_size=config.breakpoint_label_font_size),
        class_='label'
    )
    y += config.breakpoint_label_font_size / 2 + config.padding

    g.add(t)

    r = canvas.rect((0, y), (width, height - y), stroke=config.breakpoint_color, fill='none')
    r.dasharray(config.breakpoint_stroke_dasharray)
    g.add(r)

    if breakpoint.orient == ORIENT.LEFT:
        l = canvas.line((0, y), (0, height))
        l.stroke(config.breakpoint_color, width=config.breakpoint_orient_stroke_width)
        g.add(l)
    elif breakpoint.orient == ORIENT.RIGHT:
        l = canvas.line((width, y), (width, height))
        l.stroke(config.breakpoint_color, width=config.breakpoint_orient_stroke_width)
        g.add(l)
    g.add(Tag('title', 'Breakpoint {}:g.{}_{}{} {}'.format(
        breakpoint.chr, breakpoint.start, breakpoint.end, breakpoint.strand, breakpoint.orient)))
    return g


def draw_exon(config, canvas, exon, width, height, fill, label='', translation=None):
    """
    generates the svg object representing an exon

    Args:
        canvas (svgwrite.drawing.Drawing): the main svgwrite object used to create new svg elements
        exon (Exon): the exon to draw
        width (int): the pixel width
        height (int): the pixel height
        fill (str): the fill color to use for the exon

    Return:
        svgwrite.container.Group: the group element for the diagram

    .. todo::
        add markers for exons with abrogated splice sites
    """
    g = canvas.g(class_='exon')
    label = str(label)
    g.add(canvas.rect((0, 0), (width, height), fill=fill))
    t = canvas.text(
        label,
        insert=(width / 2, height / 2 + config.font_central_shift_ratio * config.exon_font_size),
        fill=config.label_color if not config.dynamic_labels else dynamic_label_color(fill),
        style=config.font_style.format(font_size=config.exon_font_size, text_anchor='middle'),
        class_='label'
    )
    g.add(t)
    title = 'Exon {}  g.{}_{}'.format(
        exon.name if exon.name else '', exon.start, exon.end)
    if translation:
        cds_start = translation.convert_genomic_to_cds_notation(exon.start)
        cds_end = translation.convert_genomic_to_cds_notation(exon.end)
        if exon.get_strand() == STRAND.NEG:
            cds_start, cds_end = cds_end, cds_start
        title += '  c.{}_{}'.format(cds_start, cds_end)
        try:
            cdna_start = translation.transcript.convert_genomic_to_cdna(exon.start)
            cdna_end = translation.transcript.convert_genomic_to_cdna(exon.end)
            if cdna_end < cdna_start:
                cdna_start, cdna_end = cdna_end, cdna_start
            title += '  cdna({}_{})'.format(cdna_start, cdna_end)
        except IndexError:
            title += '  cdna(N/A)'
    title += '  length({})'.format(len(exon))
    g.add(Tag('title', title))
    return g


def draw_template(config, canvas, template, target_width, labels=None, colors=None, breakpoints=None):
    """
    Creates the template/chromosome illustration

    Return:
        svgwrite.container.Group: the group element for the diagram
    """

    labels = LabelMapping() if labels is None else labels
    colors = {} if colors is None else colors
    breakpoints = [] if not breakpoints else breakpoints
    total_height = config.template_track_height + config.breakpoint_top_margin + config.breakpoint_bottom_margin
    group = canvas.g(class_='template')
    # 1 as input since we don't want to change the ratio here
    mapping = generate_interval_mapping(
        template.bands, target_width, 1, config.template_band_min_width,
        start=template.start, end=template.end
    )
    scaffold = canvas.rect(
        (0, 0), (target_width, config.scaffold_height),
        fill=config.scaffold_color
    )
    group.add(scaffold)
    scaffold.translate((0, config.breakpoint_top_margin + config.template_track_height / 2 - config.scaffold_height / 2))
    label_group = canvas.g()
    label_group.add(canvas.text(
        labels.add(template, config.template_label_prefix),
        insert=(
            0 - config.padding, config.breakpoint_top_margin + config.template_track_height / 2 +
            config.font_central_shift_ratio * config.label_font_size),
        fill=config.label_color,
        style=config.font_style.format(font_size=config.label_font_size, text_anchor='end'),
        class_='label'
    ))
    label_group.add(Tag('title', 'template {}'.format(template.name)))
    group.add(label_group)

    for band in template.bands:
        s = Interval.convert_pos(mapping, band[0])
        t = Interval.convert_pos(mapping, band[1])

        bgroup = canvas.g(class_='cytoband')
        f = config.template_band_fill.get(band.data.get('giemsa_stain', None), config.template_default_fill)
        r = None
        w = t - s + 1
        if band.data.get('giemsa_stain', None) == GIEMSA_STAIN.ACEN:
            if band.name[0] == 'p':
                r = canvas.polyline(
                    [(0, 0), (w, config.template_track_height / 2), (0, config.template_track_height)],
                    fill=f, stroke=config.template_band_stroke, stroke_width=config.template_band_stroke_width
                )
            else:
                r = canvas.polyline(
                    [(w, 0), (0, config.template_track_height / 2), (w, config.template_track_height)],
                    fill=f, stroke=config.template_band_stroke, stroke_width=config.template_band_stroke_width
                )
        else:
            r = canvas.rect(
                (0, 0), (w, config.template_track_height),
                fill=f, stroke=config.template_band_stroke, stroke_width=config.template_band_stroke_width
            )
        bgroup.add(r)
        bgroup.add(
            Tag('title', 'cytoband  {0}:y.{1}  {0}:g.{2}_{3}'.format(
                template.name, band.name, band.start, band.end)))
        bgroup.translate((s, config.breakpoint_top_margin))
        group.add(bgroup)
    # now draw the breakpoints overtop
    for i, b in enumerate(sorted(breakpoints)):
        s = Interval.convert_pos(mapping, b.start)
        t = Interval.convert_pos(mapping, b.end)
        bg = draw_breakpoint(
            config, canvas, b, abs(t - s) + 1, total_height, label=labels.add(b, config.breakpoint_label_prefix))
        bg.translate(s, 0)
        group.add(bg)
    setattr(
        group, 'height', total_height)
    return group


def draw_gene(config, canvas, gene, width, height, fill, label='', reference_genome=None):
    """
    generates the svg object representing a gene

    Args:
        canvas (svgwrite.drawing.Drawing): the main svgwrite object used to create new svg elements
        gene (Gene): the gene to draw
        width (int): the pixel width
        height (int): the pixel height
        fill (str): the fill color to use for the gene

    Return:
        svgwrite.container.Group: the group element for the diagram
    """

    group = canvas.g(class_='gene')
    if width < config.gene_min_width:
        raise DrawingFitError('width of {} is not sufficient to draw a gene of minimum width {}'.format(
            width, config.gene_min_width), gene)
    wrect = width - config.gene_arrow_width
    if wrect < 1:
        raise DrawingFitError('width is not sufficient to draw gene')

    label_color = config.label_color if not config.dynamic_labels else dynamic_label_color(fill)

    if gene.get_strand() == STRAND.POS:
        group.add(
            canvas.rect(
                (0, 0), (wrect, height), fill=fill
            ))
        group.add(
            canvas.polyline(
                [(wrect, 0), (wrect + config.gene_arrow_width, height / 2), (wrect, height)],
                fill=fill
            ))
        group.add(
            canvas.text(
                label,
                insert=(wrect / 2, height / 2 + config.font_central_shift_ratio * config.label_font_size),
                fill=label_color,
                style=config.font_style.format(font_size=config.label_font_size, text_anchor='middle'),
                class_='label'
            ))
    elif gene.get_strand() == STRAND.NEG:
        group.add(
            canvas.rect(
                (config.gene_arrow_width, 0), (wrect, height), fill=fill
            ))
        group.add(
            canvas.polyline(
                [(config.gene_arrow_width, 0), (0, height / 2), (config.gene_arrow_width, height)],
                fill=fill
            ))
        group.add(
            canvas.text(
                label,
                insert=(
                    wrect / 2 + config.gene_arrow_width,
                    height / 2 + config.font_central_shift_ratio * config.label_font_size
                ),
                fill=label_color,
                style=config.font_style.format(font_size=config.label_font_size, text_anchor='middle'),
                class_='label'
            ))
    else:
        group.add(
            canvas.rect(
                (0, 0), (width, height), fill=fill
            ))
        group.add(
            canvas.text(
                label,
                insert=(width / 2, height / 2 + config.font_central_shift_ratio * config.label_font_size),
                fill=label_color,
                style=config.font_style.format(font_size=config.label_font_size, text_anchor='middle'),
                class_='label'
            ))
    aliases = ''
    try:
        if gene.aliases:
            aliases = ' aka {}'.format(';'.join(sorted(gene.aliases)))
    except AttributeError:
        pass
    group.add(
        Tag('title', 'Gene {} {}:g.{}_{}{}{}'.format(gene.name if gene.name else '',
                                                     gene.chr, gene.start, gene.end, gene.get_strand(), aliases)))
    return group
