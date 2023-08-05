
Examples of the *mgkit.db* package
==================================

Imports
-------

.. code:: ipython2

    from mgkit.io import gff
    import mgkit.net
    from mgkit.db import dbm
    from mgkit.db import mongo
    import mgkit.taxon
    import gzip

Download Example GFF
--------------------

.. code:: ipython2

    # This will just load the data from the repository and save it in the same directory as
    # this notebook
    data = mgkit.net.url_read('https://bitbucket.org/setsuna80/mgkit/downloads/assembly.gff.gz')
    # The data is compressed
    open('assembly.gff.gz', 'w').write(data)

GFF Annotations
---------------

The are a few ways to load the GFF, but the result of *parse\_gff* is a
generator that yields one annotation at a time when it's iterate over.
One way to keep the annotations in memory is building a dictionary, with
the unique identifier for each annotation (called **uid**) used as key,
while the annotation object is the value.

.. code:: ipython2

    # *mgkit.io.gff.parse_gff* can read compressed data, gzip, bz2 (also lzma on python3)
    annotations = {
        annotation.uid: annotation
        for annotation in gff.parse_gff('assembly.gff.gz')
    }

Each annotation is parsed and an instance of the
**mgkit.io.gff.Annotation** is created. The class contains several
properties, like the unique identifier (uid), the gene identifier
(gene\_id) and the taxon identifier (taxon\_id)

.. code:: ipython2

    annotation = annotations['d002b31c-1d78-438c-b8f9-aba791807724']
    print annotation
    
    print annotation.uid, annotation.gene_id, annotation.taxon_id


.. parsed-literal::

    NODE_57290(-):1-87
    d002b31c-1d78-438c-b8f9-aba791807724 Q72QU2 2


Other properties and methods can be accessed, like the
*Annotation.get\_mappings* to get a dictionary of all mappings, or using
the *len* function on the instance to get it's length (or using the
property *length*).

.. code:: ipython2

    print len(annotation), annotation.length
    print annotation.get_mappings()


.. parsed-literal::

    87 87
    {'ko': ['K03695']}


Taxonomy and Annotations
~~~~~~~~~~~~~~~~~~~~~~~~

When using metagenomics, one of the problem is associated functionality
to taxonomy. MGKit contains a class that can read the taxonomy from
`Uniprot <www.uniprot.org>`__, which is compatible with NCBI taxonomy.
The **mgkit.taxon** contains the **UniprotTaxonomy** that is use to
store and in part search the taxonomy. The module contains many more
functions to resolve different levels of the taxonomy. A few examples
applied to the annotations loaded follow.

.. code:: ipython2

    # This will just load the data from the repository and save it in the same directory as
    # this notebook
    data = mgkit.net.url_read(
        "https://bitbucket.org/setsuna80/mgkit/downloads/taxonomy.pickle.gz"
    )
    open('taxonomy.pickle.gz', 'w').write(data)
    del data

.. code:: ipython2

    # Using compress taxonomy files makes it slower to load
    taxonomy = mgkit.taxon.UniprotTaxonomy('taxonomy.pickle.gz')

.. code:: ipython2

    # to find the Bacteoidales taxon identifier
    taxonomy.find_by_name('bacteroidales')




.. parsed-literal::

    [171549]



.. code:: ipython2

    # to find all the annotations that belong to the Order Bacteroidales
    count = 0
    for annotation in annotations.itervalues():
        if mgkit.taxon.is_ancestor(taxonomy, annotation.taxon_id, 171549):
            count += 1
            print annotation.uid, annotation.gene_id
    print "Number of annotation:", count


.. parsed-literal::

    7233587c-b80d-4908-8ead-92734deeec81 Q7MV19
    5322b316-46e5-44cf-9eb1-ef94355c7855 Q01VN6
    a7308f6f-7b17-4b00-8afa-92ebecef3dd3 Q8XP14
    195118b7-1236-48ad-8812-e0ec3100e7d9 Q7MV19
    14b3cc41-050a-4949-b085-75db0cda12ec Q8A294
    d1dad026-09ac-48e4-95fe-158e39d96a0d P49008
    01b819f8-1444-4f25-a3fa-93e160fa58c2 Q7MVL1
    4b3ce614-cc8a-47ea-a046-f9ca7c7ab16c Q5LI72
    65bae5c6-0d23-4a08-ae3f-aec2763f4621 Q7MV19
    3aef43ea-4e94-4940-bf85-743950e5ad8a Q9AGG3
    16794c3c-97b8-4453-8d14-a5e37c8969b4 A6LB11
    bd92adff-b8d9-411f-9488-7604eb580fd6 Q89YZ6
    3441f906-f63d-45fe-a4e5-e639439d19db A6LD25
    cd08ae89-1f1e-4875-851e-c0c55de8c764 A6LA51
    b3bf4054-4f31-4a8a-bf19-fd0e65c56867 A6LI30
    44bdfb77-1606-4194-b410-9a22c75b3b5b Q7MV19
    3b5e126e-25ec-460d-a439-2520bebe0a3d A6KZH6
    e908c5b1-9dec-4406-b952-009aab3fd778 A6LDS1
    b425ef29-0bc0-4de7-ad96-abe5c7b75f96 Q8A9M7
    2a3558c3-6f7b-49a4-a8d3-c2b0cef287d6 Q7MXZ1
    376d70e0-6591-4b2b-9a06-1d9fb7fdbc66 Q7M9Y2
    ff7fd5ef-9be2-404c-8137-89f368071a4e Q8A294
    2665ff2c-4e9a-4c7a-9604-8433fa2ae202 A6LHY5
    dd9a44d5-ed1e-4350-b05c-f0cfd510e669 A6L170
    255e75a1-a59c-43fd-9396-17a3566b3063 Q8A0F5
    49474358-7962-4b0c-b52a-5de935f17bfc A6LFA6
    27eb1efe-ff07-401c-93db-958a38e866bc Q7MWM7
    746805f5-0fdc-4499-953f-7be496b9c784 Q7MU65
    e3be2158-c013-4e58-a073-ab8e3c893094 Q8A8Y4
    e028b0e9-802f-4f1b-b055-f5ecca786170 Q8A1D3
    f2919fc6-d8e2-4fe7-ac9f-152c46d0ebbb Q7MV19
    b65468b2-d4e7-456b-871d-9cd96fa4dd48 Q02XT4
    e1643d1d-12c3-4397-a6a7-d2a24f203c4a Q8A294
    0d9cd52c-5969-49f7-866c-e8c5c9783b79 Q8A294
    cdd362ba-448f-475f-a638-d6473b471572 A6LD68
    7af092eb-20c5-46b4-b8bb-e9b0c99a8ce5 Q5LGH0
    2d9172a4-fe51-4baa-a8fb-66f020ba6452 Q7MVL1
    Number of annotation: 37


.. code:: ipython2

    # to find out the Phyla represented in the annotations
    print set(
        taxonomy.get_ranked_taxon(annotation.taxon_id, rank='phylum').s_name
        for annotation in annotations.itervalues()
    )   


.. parsed-literal::

    set(['arthropoda', 'microsporidia', 'korarchaeota', 'viruses', 'nematoda', 'bacteroidetes', 'nanoarchaeota', 'tenericutes', 'thermotogae', 'chlorophyta', 'cellular organisms', 'fibrobacteres', 'bacteria', 'euryarchaeota', 'verrucomicrobia', 'annelida', 'eukaryota', 'aquificae', 'ascomycota', 'actinobacteria', 'chlorobi', 'deferribacteres', 'archaea', 'bacillariophyta', 'streptophyta', 'chlamydiae', 'apicomplexa', 'dictyoglomi', 'cloacimonetes', 'gemmatimonadetes', 'thaumarchaeota', 'proteobacteria', 'acidobacteria', 'spirochaetes', 'cyanobacteria', 'firmicutes', 'chloroflexi', 'planctomycetes', 'chordata', 'euglenida', 'elusimicrobia', 'basidiomycota', 'xanthophyceae', 'nitrospirae', 'fusobacteria', 'deinococcus-thermus', 'platyhelminthes', 'crenarchaeota'])


.. code:: ipython2

    # to get the lineage of the first annotations
    annotation = annotations['b97ead95-81a7-4caf-8d25-349ee6e276c1']
    print taxonomy[annotation.taxon_id].s_name, mgkit.taxon.get_lineage(taxonomy, annotation.taxon_id)


.. parsed-literal::

    escherichia coli (strain k12) [131567, 2, 1224, 1236, 91347, 543, 561, 562]


.. code:: ipython2

    # to get the names, quickly
    annotation = annotations['b97ead95-81a7-4caf-8d25-349ee6e276c1']
    print taxonomy[annotation.taxon_id].s_name, mgkit.taxon.get_lineage(taxonomy, annotation.taxon_id, names=True)


.. parsed-literal::

    escherichia coli (strain k12) ['cellular organisms', 'bacteria', 'proteobacteria', 'gammaproteobacteria', 'enterobacteriales', 'enterobacteriaceae', 'escherichia', 'escherichia coli']


Issues
~~~~~~

Keeping the annotations in memory can lead to a high memory usage, as
well as a long time traversing all of them to specifically filter them.
MGKit uses two solutions to interface with DBs, one is using a
*dbm-like* database, *semidbm* and the other is using *MongoDB*.

semidbm
-------

Packages to use *dbm* database are included with Python, but they depend
on the type of OS python is installed onto. A pure Python implementation
of a dbm is `semidbm <https://github.com/jamesls/semidbm>`__. As other
*dbm*, it works in a similar way as a dictionary, while keeping the
memory usage low. To create a *semidbm* DB from annotations, the
**get-gff-info** can be used, using the **dbm** command:

.. code:: ipython2

    !get-gff-info dbm -d assembly-db assembly.gff.gz 


.. parsed-literal::

    assembly-db
    INFO - mgkit.db.dbm: DB "assembly-db" opened/created
    INFO - mgkit.io.gff: Loading GFF from file (assembly.gff.gz)


or interactively, using *mgkit.db.dbm.create\_gff\_dbm*:

.. code:: ipython2

    db = dbm.create_gff_dbm(annotations.itervalues(), 'assembly-db')


.. parsed-literal::

    assembly-db


Which also return an instance of db. *semidbm* allows the use of only
strings as keys and strings as values, so for the same annotation as
before, you see what MGKit stores in it, the actual GFF line:

.. code:: ipython2

    db['d002b31c-1d78-438c-b8f9-aba791807724']




.. parsed-literal::

    'NODE_57290\tBLAST\tCDS\t1\t87\t51.6\t-\t0\tSRR001322_cov="0";SRR001323_cov="0";SRR001325_cov="3";SRR001326_cov="0";bitscore="51.6";cov="3";db="UNIPROT-SP";dbq="10";exp_nonsyn="200";exp_syn="61";gene_id="Q72QU2";identity="75.9";map_KO="K03695";taxon_db="NCBI-NT";taxon_id="2";uid="d002b31c-1d78-438c-b8f9-aba791807724"\n'



The GFF line must then be converted back into an **Annotation**
instance. To automate the process, the **mgkit.db.dbm.GFFDB** class
wraps the *semidbm*. The same example as the one above:

.. code:: ipython2

    db = dbm.GFFDB('assembly-db')
    db['d002b31c-1d78-438c-b8f9-aba791807724']




.. parsed-literal::

    NODE_57290(-):1-87



It can also be iterated over as a dictionary (for compatibility, both
*iteritems* and *items* return an iterator)

.. code:: ipython2

    for uid in db.db:
        print uid, db[uid]
        break


.. parsed-literal::

    50dccb4d-3a49-41ed-bf8c-a1906172d8a5 NODE_49806(+):3-116


.. code:: ipython2

    for uid, annotation in db.iteritems():
        print uid, annotation
        break


.. parsed-literal::

    50dccb4d-3a49-41ed-bf8c-a1906172d8a5 NODE_49806(+):3-116


Using this class, it is possible to use a DB as a drop-in replacement
for a dictionary in a script that used annotations stored in memory in
MGKit. The `examples using the taxonomy <#Taxonomy-and-Annotations>`__
will works in the same way, for example.

Using MongoDB
-------------

`MongoDB <https://www.mongodb.org/>`__ is Document based DB that is not
based on SQL. One of the advantage of it the absence of a schema, which
makes it easy to insert annotations into it. Moreover, the data in a
MongoDB is easily accessible from a variety of programming languages, as
well as its own shell. Another advantage is the possiblity to query the
annotations and index specific values to speed up them.

In the same way as with *dbm*, the **get-gff-info** can help produce a
file that can be directly loaded into a *mongod* instance.

The following example uses **pymongo** (the official client library for
Python) and requires a **mongod** instance running on the same machine.
The annotations will be imported into the **test** database, into the
**gff** collection.

.. code:: ipython2

    !gunzip -c assembly.gff.gz | get-gff-info mongodb | mongoimport --db test --collection gff --drop


.. parsed-literal::

    2015-12-04T15:38:41.355+1000	connected to: localhost
    2015-12-04T15:38:41.355+1000	dropping: test.gff
    INFO - mgkit.io.gff: Loading GFF from file (<stdin>)
    2015-12-04T15:38:43.830+1000	imported 9135 documents


You can use the **pymongo** module directly or just use the
**mgkit.db.mongo.GFFDB** class to automate connection and conversion of
the **JSON** documents back into **Annotation** objects.

.. code:: ipython2

    db = mongo.GFFDB('test', 'gff')

.. code:: ipython2

    for annotation in db.find_annotation():
        print annotation.uid, annotation.gene_id
        break


.. parsed-literal::

    303fbf1f-8140-4f9e-9c44-ae089e67bdc3 O93746


The DB can be queried by passing the **GFF.find\_annotation** method the
same query that are explained in `Pymongo
documentation <https://docs.mongodb.org/getting-started/python/client/>`__.

.. code:: ipython2

    # To look for all annotations that have the KO mapping to K01883
    for annotation in db.find_annotation({'map.ko': 'K01883'}):
        print annotation


.. parsed-literal::

    NODE_22940(-):2-97
    NODE_8691(+):2-88
    NODE_8691(+):5-91
    NODE_30222(+):11-97
    NODE_30222(+):2-82
    NODE_30222(+):8-94
    NODE_30222(+):5-91
    NODE_36783(+):11-115
    NODE_2009(-):3-104
    NODE_2009(-):12-110
    NODE_19876(+):3-113
    NODE_35927(-):2-76
    NODE_35927(-):8-163
    NODE_31317(+):2-73
    NODE_31317(+):5-88
    NODE_29415(+):29-100
    NODE_45868(-):1-96
    NODE_1013(-):33-128
    NODE_39238(-):1-90
    NODE_39238(-):4-93
    NODE_6581(-):3-116
    NODE_40758(-):2-163
    NODE_7805(-):1-117
    NODE_28135(+):3-116
    NODE_8575(+):34-123
    NODE_8575(+):28-114
    NODE_6979(+):1-99
    NODE_35052(-):2-106
    NODE_13245(-):2-94
    NODE_13245(-):5-97
    NODE_30508(+):1-99
    NODE_19190(+):18-227
    NODE_19190(+):3-113
    NODE_16671(+):2-106


.. code:: ipython2

    # To look for all annotations that have the KO mapping to K01883 *AND*
    # the taxonomy was inferred from a blast to NCBI (see refinement of
    # taxonomy in theTutorial - Gene Prediction)
    for annotation in db.find_annotation({'map.ko': 'K01883', 'taxon_db': 'NCBI-NT'}):
        print annotation


.. parsed-literal::

    NODE_22940(-):2-97
    NODE_30222(+):11-97
    NODE_30222(+):2-82
    NODE_30222(+):8-94
    NODE_30222(+):5-91
    NODE_40758(-):2-163


.. code:: ipython2

    # Finding all annotation from a specific taxon
    for annotation in db.find_annotation({'taxon_id': 224911}):
        print annotation


.. parsed-literal::

    NODE_36848(-):2-94
    NODE_58432(+):8-124
    NODE_48731(+):5-118
    NODE_13988(+):20-190
    NODE_10564(-):3-101
    NODE_61599(+):8-106
    NODE_58191(+):1-99
    NODE_36561(+):5-115
    NODE_33951(-):13-99
    NODE_20537(-):6-101
    NODE_72294(-):3-95


Using Taxonomy
~~~~~~~~~~~~~~

The usual approach about the taxonomy is to traverse all the annotations
(those returned by one of the previous queries, even) and use the
functionality in the **mgkit.taxon** module. It is possible to repeat
the example that search all annotations that belong to Order
*Bacteroidales*, but the records must be loaded with the lineage into
the DB. This can be done having a taxonomy file, *taxonomy.pickle.gz* in
our case, with the following command:

.. code:: ipython2

    !gunzip -c assembly.gff.gz | get-gff-info mongodb -t taxonomy.pickle.gz | mongoimport --db test --collection gff --drop


.. parsed-literal::

    2015-12-04T16:32:13.785+1000	connected to: localhost
    2015-12-04T16:32:13.786+1000	dropping: test.gff
    2015-12-04T16:32:16.783+1000	test.gff	0.0 B
    2015-12-04T16:32:19.783+1000	test.gff	0.0 B
    INFO - mgkit.taxon: Loading taxonomy from file taxonomy.pickle.gz
    2015-12-04T16:32:22.785+1000	test.gff	0.0 B
    2015-12-04T16:32:25.782+1000	test.gff	0.0 B
    2015-12-04T16:32:28.784+1000	test.gff	0.0 B
    2015-12-04T16:32:31.780+1000	test.gff	0.0 B
    2015-12-04T16:32:34.783+1000	test.gff	0.0 B
    2015-12-04T16:32:37.780+1000	test.gff	0.0 B
    2015-12-04T16:32:40.782+1000	test.gff	0.0 B
    2015-12-04T16:32:43.782+1000	test.gff	0.0 B
    2015-12-04T16:32:46.785+1000	test.gff	0.0 B
    2015-12-04T16:32:49.785+1000	test.gff	0.0 B
    2015-12-04T16:32:52.783+1000	test.gff	0.0 B
    2015-12-04T16:32:55.783+1000	test.gff	0.0 B
    2015-12-04T16:32:58.781+1000	test.gff	0.0 B
    2015-12-04T16:33:01.780+1000	test.gff	0.0 B
    2015-12-04T16:33:04.783+1000	test.gff	0.0 B
    2015-12-04T16:33:07.781+1000	test.gff	0.0 B
    2015-12-04T16:33:10.781+1000	test.gff	0.0 B
    2015-12-04T16:33:13.781+1000	test.gff	0.0 B
    2015-12-04T16:33:16.781+1000	test.gff	0.0 B
    2015-12-04T16:33:19.783+1000	test.gff	0.0 B
    2015-12-04T16:33:22.781+1000	test.gff	0.0 B
    2015-12-04T16:33:25.782+1000	test.gff	0.0 B
    2015-12-04T16:33:28.781+1000	test.gff	0.0 B
    2015-12-04T16:33:31.783+1000	test.gff	0.0 B
    2015-12-04T16:33:34.785+1000	test.gff	0.0 B
    2015-12-04T16:33:37.781+1000	test.gff	0.0 B
    2015-12-04T16:33:40.780+1000	test.gff	0.0 B
    2015-12-04T16:33:43.782+1000	test.gff	0.0 B
    2015-12-04T16:33:46.780+1000	test.gff	0.0 B
    2015-12-04T16:33:49.780+1000	test.gff	0.0 B
    2015-12-04T16:33:52.781+1000	test.gff	0.0 B
    2015-12-04T16:33:55.782+1000	test.gff	0.0 B
    2015-12-04T16:33:58.785+1000	test.gff	0.0 B
    2015-12-04T16:34:01.784+1000	test.gff	0.0 B
    2015-12-04T16:34:04.781+1000	test.gff	0.0 B
    2015-12-04T16:34:07.782+1000	test.gff	0.0 B
    2015-12-04T16:34:10.785+1000	test.gff	0.0 B
    2015-12-04T16:34:13.781+1000	test.gff	0.0 B
    2015-12-04T16:34:16.784+1000	test.gff	0.0 B
    2015-12-04T16:34:19.783+1000	test.gff	0.0 B
    2015-12-04T16:34:22.780+1000	test.gff	0.0 B
    2015-12-04T16:34:25.785+1000	test.gff	0.0 B
    2015-12-04T16:34:28.781+1000	test.gff	0.0 B
    2015-12-04T16:34:31.780+1000	test.gff	0.0 B
    2015-12-04T16:34:34.783+1000	test.gff	0.0 B
    2015-12-04T16:34:37.780+1000	test.gff	0.0 B
    2015-12-04T16:34:40.782+1000	test.gff	0.0 B
    2015-12-04T16:34:43.781+1000	test.gff	0.0 B
    2015-12-04T16:34:46.785+1000	test.gff	0.0 B
    INFO - mgkit.workflow.extract_gff_info: Using cached calls to lineage
    INFO - mgkit.io.gff: Loading GFF from file (<stdin>)
    2015-12-04T16:34:49.783+1000	test.gff	2.7 MB
    2015-12-04T16:34:51.874+1000	imported 9135 documents


The script will first load the taxonomy and add to each record in the
database the **lineage** key. This contains an array of integers, that
are the output of the **mgkit.taxon.lineage** function and can be
searched using:

.. code:: ipython2

    count = 0
    for annotation in db.find_annotation({'lineage': 171549}):
        count += 1
        print annotation
    print "Number of annotation:", count


.. parsed-literal::

    NODE_33533(-):2-64
    NODE_18827(+):2-127
    NODE_25363(+):3-95
    NODE_69486(+):1-111
    NODE_13380(-):3-95
    NODE_8404(+):3-176
    NODE_71367(+):2-106
    NODE_50779(-):1-102
    NODE_20694(+):129-221
    NODE_38976(+):4-102
    NODE_69904(+):9-110
    NODE_1963(-):2-94
    NODE_41194(-):18-98
    NODE_47622(+):1-99
    NODE_56590(+):2-103
    NODE_66803(+):23-169
    NODE_14043(+):4-96
    NODE_35099(+):18-122
    NODE_48598(-):20-97
    NODE_58511(+):1-96
    NODE_70185(+):2-103
    NODE_56348(-):4-93
    NODE_56348(-):13-102
    NODE_56348(-):10-99
    NODE_32336(-):1-114
    NODE_59685(+):3-107
    NODE_57945(+):12-134
    NODE_59259(-):1-108
    NODE_28794(-):5-133
    NODE_72312(-):1-96
    NODE_37438(+):3-107
    NODE_6370(+):123-224
    NODE_67647(+):2-100
    NODE_28480(-):1-93
    NODE_72226(+):8-103
    NODE_46503(+):3-104
    NODE_20236(+):1-90
    Number of annotation: 37


And as you can see, the number of annotations is the same as the
`example above <#Taxonomy-and-Annotations>`__. The use of MongoDB to
store the annotations can make it simplier to use richer queries, even
from other languages.
