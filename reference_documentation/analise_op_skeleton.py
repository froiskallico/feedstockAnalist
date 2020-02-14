ops = (1, 2, 3)

mps_falta = ()

for op in ops:
    chicotes = SELECT chicotes, quantidade FROM ite_ose WHERE pk_ose = op

    for chicote in chicotes:
        mps = SELECT cpd, qtd_fic FROM fic_tec WHERE pk_pro = chicote

        for mp in mps:
            ops = SELET op, quantidade FROM ops_from_mp WHERE mp = mp
            ocs = SELET op, quantidade FROM ocs_from_mp WHERE mp = mp

            datas_falta = confronta_ops_ocs();

            if len(datas_falta) > 0:
                mps_falta.append(mp)

            for data in datas_falta:
                ops_falta, clientes_falta, quantidade = SELECT op, cliente, quantidade, FROM ops WHERE ops.entrega > data;

            ocs_futuras = SELECT oc FROM ocs WHERE ocs.entrega > datas_falta;

            if len(ocs_futuras) > 0:
                sugestao = antecipar(ocs_futuras)
            else:
                sugestao = comprar(quantidade)

            if min(data_falta) < mp.lead_time:
                alerta_leadtime()
            








