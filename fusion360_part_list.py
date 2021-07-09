import adsk.core
import adsk.fusion
from collections import defaultdict

# Fusion 360 parts list with dimensions
# API manual https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-C1545D80-D804-4CF3-886D-9B5C54B2D7A2


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    units = design.unitsManager.defaultLengthUnits
    # Get the root component of the active design.
    rootComp = design.rootComponent

    # Get occurences from root
    components = [rootComp.occurrences[i].component for i in range(
        rootComp.occurrences.count)]
    components = [rootComp] + components

    total_lengths = defaultdict(float)
    total_counts = defaultdict(int)

    dialog_str = ''
    dialog_str += '<table>'
    dialog_str += '<tr>'
    dialog_str += '<th style="text-align:left;">Component</th>'
    dialog_str += '<th style="text-align:left;">Body</th>'
    dialog_str += f'<th style="text-align:right;">x ({units})</th>'
    dialog_str += f'<th style="text-align:right;">y ({units})</th>'
    dialog_str += f'<th style="text-align:right;">z ({units})</th>'
    dialog_str += '</tr>'

    not_visible_count = 0

    for subcomp in components:
        for bidx in range(0, subcomp.bRepBodies.count):
            body = subcomp.bRepBodies.item(bidx)

            if not body.isVisible:
                not_visible_count += 1
                continue

            dimvector = body.boundingBox.minPoint.vectorTo(
                body.boundingBox.maxPoint).asPoint()
            dims = sorted(dimvector.asArray())

            formx = product.unitsManager.formatInternalValue(
                dims[0], units, False)
            formy = product.unitsManager.formatInternalValue(
                dims[1], units, False)
            formz = product.unitsManager.formatInternalValue(
                dims[2], units, False)

            dialog_str += '<tr>'
            dialog_str += f'<td style="text-align:left;padding-right:15px">{subcomp.name}</td>'
            dialog_str += f'<td style="text-align:left;padding-right:15px">{body.name}</td>'
            dialog_str += f'<td style="text-align:right;padding-left: 15px;">{formx}</td>'
            dialog_str += f'<td style="text-align:right;padding-left: 15px;">{formy}</td>'
            dialog_str += f'<td style="text-align:right;padding-left: 15px;">{formz}</td>'
            dialog_str += '</tr>'

            key_length = f'{formx} x {formy}'
            total_lengths[key_length] += float(formz)

            key_count = f'{formx} x {formy} x {formz}'
            total_counts[key_count] += 1

    dialog_str += '</table>'

    dialog_str += '<h2>Total counts</h2>'
    dialog_str += '<table>'
    dialog_str += '<tr>'
    dialog_str += '<th style="text-align:left;">Dimensions</th>'
    dialog_str += '<th style="text-align:right;">Count</th></tr>'

    for key_count in sorted(total_counts.keys()):
        dialog_str += f'<tr>'
        dialog_str += f'<td style="text-align:left;padding-right:15px">{key_count}</td>'
        dialog_str += f'<td style="text-align:right;padding-left:15px">{total_counts[key_count]}</td>'
        dialog_str += '</tr>'
    dialog_str += '</table>'

    dialog_str += '<h2>Total lengths</h2>'
    dialog_str += '<table>'
    dialog_str += '<tr>'
    dialog_str += f'<th style="text-align:left;">Dimensions ({units})</th>'
    dialog_str += f'<th style="text-align:right;">Total length ({units})</th>'
    dialog_str += '</tr>'

    for key_length in sorted(total_lengths.keys()):
        dialog_str += f'<tr>'
        dialog_str += f'<td style="text-align:left;padding-right:15px">{key_length}</td>'
        dialog_str += f'<td style="text-align:right;padding-left:15px">{total_lengths[key_length]}</td>'
        dialog_str += '</tr>'
    dialog_str += '</table>'

    if not_visible_count:
        dialog_str += f'<br/><br/><i>Note: {not_visible_count} hidden {"body" if not_visible_count == 1 else "bodies"} excluded from the lists</i>'

    ui.messageBox(dialog_str, 'Total materials used', adsk.core.MessageBoxButtonTypes.OKButtonType,
                  adsk.core.MessageBoxIconTypes.InformationIconType)
    print(dialog_str)
