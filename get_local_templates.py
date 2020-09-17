for hi in dmd.Devices.Database.Oracle.Base.getSubDevices():
    if '2128' in hi.getDeviceClassName():
        checked = False
        print 'CI : {}'.format(hi.getId())
        templates = hi.getRRDTemplates()
        for tmpl in templates:
            if hi.getId() in tmpl.getRRDPath():
                print '\tDevice template {} is bound locally'.format(tmpl.getId())
                checked = True
        for comp in hi.getDeviceComponents():
            for comp_template in comp.getRRDTemplates():
                if hi.getId() in comp_template.getRRDPath():
                    print '\t{} is bound locally for component {}'.format(comp_template.getId(), comp.getId())
                    checked = True
        if not checked:
            print 'Nothing locally modified.\n'
