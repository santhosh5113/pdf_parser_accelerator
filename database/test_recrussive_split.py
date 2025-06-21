from database.text_chunker import chunk_text_with_strategy

# Replace this with your actual input text or load from a file
input_text = """schema_name": "DoclingDocument",
  "version": "1.4.0",
  "name": "only_text",
  "origin": {
    "mimetype": "application/pdf",
    "binary_hash": 7579087746992301621,
    "filename": "only_text.pdf"
  },
  "furniture": {
    "self_ref": "#/furniture",
    "children": [],
    "content_layer": "furniture",
    "name": "_root_",
    "label": "unspecified"
  },
  "body": {
    "self_ref": "#/body",
    "children": [
      {
        "$ref": "#/pictures/0"
      },
      {
        "$ref": "#/texts/0"
      },
      {
        "$ref": "#/pictures/1"
      },
      {
        "$ref": "#/texts/1"
      },
      {
        "$ref": "#/texts/2"
      },
      {
        "$ref": "#/pictures/2"
      },
      {
        "$ref": "#/texts/3"
      },
      {
        "$ref": "#/texts/4"
      },
      {
        "$ref": "#/groups/0"
      },
      {
        "$ref": "#/texts/10"
      },
      {
        "$ref": "#/texts/11"
      },
      {
        "$ref": "#/texts/12"
      },
      {
        "$ref": "#/groups/1"
      },
      {
        "$ref": "#/groups/2"
      },
      {
        "$ref": "#/texts/16"
      },
      {
        "$ref": "#/texts/17"
      },
      {
        "$ref": "#/texts/18"
      },
      {
        "$ref": "#/texts/19"
      },
      {
        "$ref": "#/texts/20"
      },
      {
        "$ref": "#/texts/21"
      },
      {
        "$ref": "#/texts/22"
      },
      {
        "$ref": "#/groups/3"
      },
      {
        "$ref": "#/texts/25"
      },
      {
        "$ref": "#/groups/4"
      },
      {
        "$ref": "#/texts/32"
      },
      {
        "$ref": "#/texts/33"
      },
      {
        "$ref": "#/texts/34"
      },
      {
        "$ref": "#/texts/35"
      },
      {
        "$ref": "#/texts/36"
      },
      {
        "$ref": "#/texts/37"
      },
      {
        "$ref": "#/texts/38"
      },
      {
        "$ref": "#/texts/39"
      },
      {
        "$ref": "#/texts/40"
      },
      {
        "$ref": "#/texts/41"
      },
      {
        "$ref": "#/texts/42"
      },
      {
        "$ref": "#/texts/43"
      },
      {
        "$ref": "#/texts/44"
      },
      {
        "$ref": "#/texts/45"
      },
      {
        "$ref": "#/texts/46"
      },
      {
        "$ref": "#/texts/47"
      },
      {
        "$ref": "#/texts/48"
      },
      {
        "$ref": "#/texts/49"
      },
      {
        "$ref": "#/texts/50"
      },
      {
        "$ref": "#/texts/51"
      },
      {
        "$ref": "#/texts/52"
      },
      {
        "$ref": "#/texts/53"
      },
      {
        "$ref": "#/texts/54"
      },
      {
        "$ref": "#/texts/55"
      },
      {
        "$ref": "#/texts/56"
      },
      {
        "$ref": "#/texts/57"
      },
      {
        "$ref": "#/texts/58"
      },
      {
        "$ref": "#/texts/59"
      },
      {
        "$ref": "#/texts/60"
      },
      {
        "$ref": "#/groups/5"
      },
      {
        "$ref": "#/texts/62"
      },
      {
        "$ref": "#/texts/63"
      },
      {
        "$ref": "#/texts/64"
      },
      {
        "$ref": "#/texts/65"
      },
      {
        "$ref": "#/texts/66"
      },
      {
        "$ref": "#/texts/67"
      },
      {
        "$ref": "#/texts/68"
      },
      {
        "$ref": "#/texts/69"
      },
      {
        "$ref": "#/texts/70"
      },
      {
        "$ref": "#/texts/71"
      },
      {
        "$ref": "#/texts/72"
      },
      {
        "$ref": "#/texts/73"
      },
      {
        "$ref": "#/texts/74"
      },
      {
        "$ref": "#/texts/75"
      },
      {
        "$ref": "#/texts/76"
      },
      {
        "$ref": "#/pictures/3"
      },
      {
        "$ref": "#/texts/77"
      },
      {
        "$ref": "#/texts/78"
      },
      {
        "$ref": "#/texts/79"
      },
      {
        "$ref": "#/texts/80"
      },
      {
        "$ref": "#/texts/81"
      }
    ],
    "content_layer": "body",
    "name": "_root_",
    "label": "unspecified"
  },
  "groups": [
    {
      "self_ref": "#/groups/0",
      "parent": {
        "$ref": "#/body"
      },
      "children": [
        {
          "$ref": "#/texts/5"
        },
        {
          "$ref": "#/texts/6"
        },
        {
          "$ref": "#/texts/7"
        },
        {
          "$ref": "#/texts/8"
        },
        {
          "$ref": "#/texts/9"
        }
      ],
      "content_layer": "body",
      "name": "list",
      "label": "list"
    },
    {
      "self_ref": "#/groups/1",
      "parent": {
        "$ref": "#/body"
      },
      "children": [
        {
          "$ref": "#/texts/13"
        },
        {
          "$ref": "#/texts/14"
        }
      ],
      "content_layer": "body",
      "name": "list",
      "label": "list"
    },
    {
      "self_ref": "#/groups/2",
      "parent": {
        "$ref": "#/body"
      },
      "children": [
        {
          "$ref": "#/texts/15"
        }
      ],
      "content_layer": "body",
      "name": "group",
      "label": "key_value_area"
    },
    {
      "self_ref": "#/groups/3",
      "parent": {
        "$ref": "#/body"
      },
      "children": [
        {
          "$ref": "#/texts/23"
        },
        {
          "$ref": "#/texts/24"
        }
      ],
      "content_layer": "body",
      "name": "list",
      "label": "list"
    },
    {
      "self_ref": "#/groups/4",
      "parent": {
        "$ref": "#/body"
      },
      "children": [
        {
          "$ref": "#/texts/26"
        },
        {
          "$ref": "#/texts/27"
        },
        {
          "$ref": "#/texts/28"
        },
        {
          "$ref": "#/texts/29"
        },
        {
          "$ref": "#/texts/30"
        },
        {
          "$ref": "#/texts/31"
        }
      ],
      "content_layer": "body",
      "name": "list",
      "label": "list"
    },
    {
      "self_ref": "#/groups/5",
      "parent": {
        "$ref": "#/body"
      },
      "children": [
        {
          "$ref": "#/texts/61"
        }
      ],
      "content_layer": "body",
      "name": "list",
      "label": "list"
    }
  ],
  "texts": [
    {
      "self_ref": "#/texts/0",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.956,
            "t": 781.709,
            "r": 353.284,
            "b": 768.275,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            32
          ]
        }
      ],
      "orig": "THE CENTRE FOR HUMANITARIAN DATA",
      "text": "THE CENTRE FOR HUMANITARIAN DATA",
      "level": 1
    },
    {
      "self_ref": "#/texts/1",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.31,
            "t": 739.438,
            "r": 211.418,
            "b": 728.566,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            20
          ]
        }
      ],
      "orig": "GUIDANCE NOTE SERIES",
      "text": "GUIDANCE NOTE SERIES",
      "level": 1
    },
    {
      "self_ref": "#/texts/2",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.31,
            "t": 721.438,
            "r": 378.069,
            "b": 710.566,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            42
          ]
        }
      ],
      "orig": "DATA RESPONSIBILITY IN HUMANITARIAN ACTION",
      "text": "DATA RESPONSIBILITY IN HUMANITARIAN ACTION",
      "level": 1
    },
    {
      "self_ref": "#/texts/3",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.31,
            "t": 692.436,
            "r": 519.294,
            "b": 675.152,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            36
          ]
        }
      ],
      "orig": "RESPONSIBLE DATA SHARING WITH DONORS",
      "text": "RESPONSIBLE DATA SHARING WITH DONORS",
      "level": 1
    },
    {
      "self_ref": "#/texts/4",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 63.717,
            "t": 641.989,
            "r": 167.09,
            "b": 631.982,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            14
          ]
        }
      ],
      "orig": "KEY TAKEAWAYS:",
      "text": "KEY TAKEAWAYS:",
      "level": 1
    },
    {
      "self_ref": "#/texts/5",
      "parent": {
        "$ref": "#/groups/0"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 74.981,
            "t": 619.813,
            "r": 522.775,
            "b": 597.155,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            166
          ]
        }
      ],
      "orig": "· Sharing sensitive personal and non-personal data without adequate safeguards can exacerbate risks for crisis-affected people, humanitarian organizations and donors.",
      "text": "· Sharing sensitive personal and non-personal data without adequate safeguards can exacerbate risks for crisis-affected people, humanitarian organizations and donors.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/6",
      "parent": {
        "$ref": "#/groups/0"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 74.981,
            "t": 582.413,
            "r": 526.417,
            "b": 546.555,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            236
          ]
        }
      ],
      "orig": "· Donors regularly request data from the organizations they fund in order to fulfil their obligations and objectives. Some of these requests relate to sensitive information and data which needs to be protected in order to mitigate risk.",
      "text": "· Donors regularly request data from the organizations they fund in order to fulfil their obligations and objectives. Some of these requests relate to sensitive information and data which needs to be protected in order to mitigate risk.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/7",
      "parent": {
        "$ref": "#/groups/0"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 74.981,
            "t": 531.813,
            "r": 510.488,
            "b": 495.955,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            197
          ]
        }
      ],
      "orig": "· Common objectives for data sharing with donors include: (i) situational awareness and programme design; (ii) accountability and transparency; and (iii) legal, regulatory, and policy requirements.",
      "text": "· Common objectives for data sharing with donors include: (i) situational awareness and programme design; (ii) accountability and transparency; and (iii) legal, regulatory, and policy requirements.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/8",
      "parent": {
        "$ref": "#/groups/0"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 74.981,
            "t": 479.013,
            "r": 531.708,
            "b": 443.155,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            202
          ]
        }
      ],
      "orig": "· Common constraints related to sharing data with donors include: (i) lack of regulatory framework for responsibly managing sensitive non-personal data; (ii) capacity gaps; and (iii) purpose limitation.",
      "text": "· Common constraints related to sharing data with donors include: (i) lack of regulatory framework for responsibly managing sensitive non-personal data; (ii) capacity gaps; and (iii) purpose limitation.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/9",
      "parent": {
        "$ref": "#/groups/0"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 74.981,
            "t": 428.413,
            "r": 532.788,
            "b": 366.155,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            467
          ]
        }
      ],
      "orig": "· Donors and humanitarian organizations can take the following steps to minimize risks while maximizing benefits when sharing sensitive data: (i) reviewing and clarifying the formal or informal frameworks that govern the collection and sharing of disaggregated data; (ii) formalizing and standardising requests for sensitive data; (iii) investing in data management capacities of staff and organisations; and (iv) adopting common principles for donor data management.",
      "text": "· Donors and humanitarian organizations can take the following steps to minimize risks while maximizing benefits when sharing sensitive data: (i) reviewing and clarifying the formal or informal frameworks that govern the collection and sharing of disaggregated data; (ii) formalizing and standardising requests for sensitive data; (iii) investing in data management capacities of staff and organisations; and (iv) adopting common principles for donor data management.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/10",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.531,
            "t": 328.467,
            "r": 149.482,
            "b": 318.46000000000004,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            12
          ]
        }
      ],
      "orig": "INTRODUCTION",
      "text": "INTRODUCTION",
      "level": 1
    },
    {
      "self_ref": "#/texts/11",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.454,
            "t": 304.29999999999995,
            "r": 546.789,
            "b": 215.64200000000005,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            643
          ]
        }
      ],
      "orig": "Donors have an important role in the humanitarian data ecosystem, both as drivers of increased data collection and analysis, and as direct users of data. This is not a new phenomenon; the need for accountability and transparency in the use of donor funding is broadly understood and respected. However, in recent years, donors have begun requesting data that can be sensitive. This includes personal data about beneficiaries and various forms of disaggregated data, such as household-level survey results and data about the delivery of assistance disaggregated by demographic and/or group dimensions (e.g. ethnicity, protection group, etc.). 1",
      "text": "Donors have an important role in the humanitarian data ecosystem, both as drivers of increased data collection and analysis, and as direct users of data. This is not a new phenomenon; the need for accountability and transparency in the use of donor funding is broadly understood and respected. However, in recent years, donors have begun requesting data that can be sensitive. This includes personal data about beneficiaries and various forms of disaggregated data, such as household-level survey results and data about the delivery of assistance disaggregated by demographic and/or group dimensions (e.g. ethnicity, protection group, etc.). 1"
    },
    {
      "self_ref": "#/texts/12",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.437,
            "t": 198.70600000000002,
            "r": 535.199,
            "b": 110.04899999999998,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            644
          ]
        }
      ],
      "orig": "Concerns around requests for such data have led donors and humanitarian organizations to place more emphasis on identifying strategies for data responsibility: the safe, ethical and effective management of data. Data responsibility requires donors and humanitarian organizations to take actions that help minimize risks while maximizing benefits of data. This is particularly challenging in cases where donors request sensitive data. For example, the screening of aid recipients, which is often used to justify requests for personal data, is not only difficult to practically implement, but also highly problematic in terms of principled aid. 2",
      "text": "Concerns around requests for such data have led donors and humanitarian organizations to place more emphasis on identifying strategies for data responsibility: the safe, ethical and effective management of data. Data responsibility requires donors and humanitarian organizations to take actions that help minimize risks while maximizing benefits of data. This is particularly challenging in cases where donors request sensitive data. For example, the screening of aid recipients, which is often used to justify requests for personal data, is not only difficult to practically implement, but also highly problematic in terms of principled aid. 2"
    },
    {
      "self_ref": "#/texts/13",
      "parent": {
        "$ref": "#/groups/1"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.858,
            "t": 102.74800000000005,
            "r": 535.715,
            "b": 86.83100000000002,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            299
          ]
        }
      ],
      "orig": "1 Because there are well-established and accepted standards and mechanisms for sharing financial information with donors, including a role for external audits, requests for financial data are not included in this guidance note. This guidance note deals with sensitive personal and non-personal data.",
      "text": "1 Because there are well-established and accepted standards and mechanisms for sharing financial information with donors, including a role for external audits, requests for financial data are not included in this guidance note. This guidance note deals with sensitive personal and non-personal data.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/14",
      "parent": {
        "$ref": "#/groups/1"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.857,
            "t": 81.74800000000005,
            "r": 520.657,
            "b": 65.48400000000004,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            154
          ]
        }
      ],
      "orig": "2 Roepstorff, K., Faltas, C. and Hövelmann, S., 2020. Counterterrorism Measures and Sanction Regimes: Shrinking Space for Humanitarian Aid Organisations .",
      "text": "2 Roepstorff, K., Faltas, C. and Hövelmann, S., 2020. Counterterrorism Measures and Sanction Regimes: Shrinking Space for Humanitarian Aid Organisations .",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/15",
      "parent": {
        "$ref": "#/groups/2"
      },
      "children": [],
      "content_layer": "body",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 269.777,
            "t": 47.75199999999995,
            "r": 324.927,
            "b": 40.874000000000024,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            13
          ]
        }
      ],
      "orig": "DECEMBER 2020",
      "text": "DECEMBER 2020"
    },
    {
      "self_ref": "#/texts/16",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.448,
            "t": 47.79200000000003,
            "r": 186.441,
            "b": 40.91399999999999,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            32
          ]
        }
      ],
      "orig": "THE CENTRE FOR HUMANITARIAN DATA",
      "text": "THE CENTRE FOR HUMANITARIAN DATA"
    },
    {
      "self_ref": "#/texts/17",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 537.187,
            "t": 47.60699999999997,
            "r": 541.763,
            "b": 40.418000000000006,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            1
          ]
        }
      ],
      "orig": "1",
      "text": "1"
    },
    {
      "self_ref": "#/texts/18",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 52.858,
            "t": 793.278,
            "r": 543.501,
            "b": 717.82,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            612
          ]
        }
      ],
      "orig": "In addition, sharing seemingly innocuous data such as aggregated survey results can place already vulnerable people and communities at greater risk. What may be initially considered non-personal data 3 can allow for re-identification of individuals, communities and demographic groups. Re-identification occurs when data can be traced back or linked to an individual(s) or group(s) of individuals because it is not adequately anonymized. This can result in a violation of data protection, privacy and other human rights and can allow for targeting of individuals or groups with violence or other forms of harm. 4",
      "text": "In addition, sharing seemingly innocuous data such as aggregated survey results can place already vulnerable people and communities at greater risk. What may be initially considered non-personal data 3 can allow for re-identification of individuals, communities and demographic groups. Re-identification occurs when data can be traced back or linked to an individual(s) or group(s) of individuals because it is not adequately anonymized. This can result in a violation of data protection, privacy and other human rights and can allow for targeting of individuals or groups with violence or other forms of harm. 4"
    },
    {
      "self_ref": "#/texts/19",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 52.858,
            "t": 703.078,
            "r": 530.893,
            "b": 614.42,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            692
          ]
        }
      ],
      "orig": "Many donors and humanitarian actors recognize the risks and benefits associated with sharing such sensitive data, but the sector has yet to establish a common understanding of how to balance these risks and benefits effectively. Recent efforts to address this issue have led to more clarity on current practices, as well as on the objectives and constraints of data sharing. In September 2020, the Government of Switzerland, the International Committee of the Red Cross (ICRC) and the United Nations Office for Coordination of Humanitarian Affairs (UN OCHA) Centre for Humanitarian Data (the Centre) organized a virtual Wilton Park dialogue to help build common understanding on this issue. 5",
      "text": "Many donors and humanitarian actors recognize the risks and benefits associated with sharing such sensitive data, but the sector has yet to establish a common understanding of how to balance these risks and benefits effectively. Recent efforts to address this issue have led to more clarity on current practices, as well as on the objectives and constraints of data sharing. In September 2020, the Government of Switzerland, the International Committee of the Red Cross (ICRC) and the United Nations Office for Coordination of Humanitarian Affairs (UN OCHA) Centre for Humanitarian Data (the Centre) organized a virtual Wilton Park dialogue to help build common understanding on this issue. 5"
    },
    {
      "self_ref": "#/texts/20",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 52.86,
            "t": 598.113,
            "r": 533.05,
            "b": 561.62,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            281
          ]
        }
      ],
      "orig": "This guidance note synthesizes the outcomes of this dialogue and a related desk review. 6 It describes the challenges around sharing sensitive data with donors and offers initial recommendations for how donors and humanitarian organizations can more effectively navigate this area.",
      "text": "This guidance note synthesizes the outcomes of this dialogue and a related desk review. 6 It describes the challenges around sharing sensitive data with donors and offers initial recommendations for how donors and humanitarian organizations can more effectively navigate this area."
    },
    {
      "self_ref": "#/texts/21",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 52.937,
            "t": 540.828,
            "r": 231.428,
            "b": 530.821,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            23
          ]
        }
      ],
      "orig": "DONOR REQUESTS FOR DATA",
      "text": "DONOR REQUESTS FOR DATA",
      "level": 1
    },
    {
      "self_ref": "#/texts/22",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 52.86,
            "t": 516.661,
            "r": 519.399,
            "b": 494.003,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            155
          ]
        }
      ],
      "orig": "Donors regularly request data from their partners in order to fulfil different obligations and objectives. These requests can be either formal or informal.",
      "text": "Donors regularly request data from their partners in order to fulfil different obligations and objectives. These requests can be either formal or informal."
    },
    {
      "self_ref": "#/texts/23",
      "parent": {
        "$ref": "#/groups/3"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 64.201,
            "t": 477.061,
            "r": 538.737,
            "b": 428.003,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            331
          ]
        }
      ],
      "orig": "· Formal requests tend to be included in grant agreements in relation to reporting criteria, and are typically based on legal requirements such as compliance with counter-terrorism laws. Such requests tend to be negotiated at the outset of a partnership or grant agreement, and are usually made in writing and scheduled in advance.",
      "text": "· Formal requests tend to be included in grant agreements in relation to reporting criteria, and are typically based on legal requirements such as compliance with counter-terrorism laws. Such requests tend to be negotiated at the outset of a partnership or grant agreement, and are usually made in writing and scheduled in advance.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/24",
      "parent": {
        "$ref": "#/groups/3"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 64.212,
            "t": 411.061,
            "r": 531.665,
            "b": 348.803,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            406
          ]
        }
      ],
      "orig": "· Informal requests concern information or data that typically fall outside of the normal scope  of reporting. These ad-hoc requests often carry implicit value, meaning that while they are not formally required, delivering this supplementary data is deemed beneficial for an organization's ongoing engagement and partnership with a donor. These requests represent a greater dilemma for humanitarian actors.",
      "text": "· Informal requests concern information or data that typically fall outside of the normal scope  of reporting. These ad-hoc requests often carry implicit value, meaning that while they are not formally required, delivering this supplementary data is deemed beneficial for an organization's ongoing engagement and partnership with a donor. These requests represent a greater dilemma for humanitarian actors.",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/25",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 52.861,
            "t": 332.488,
            "r": 532.666,
            "b": 282.7950000000001,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            400
          ]
        }
      ],
      "orig": "Few donors have formal data sharing policies or guidelines in place.  There is also a lack of shared 7 understanding of terminology and of the objectives and risks around data sharing. There are different definitions and understanding of data-related risks, leading to inconsistent and sometimes contradictory practices around sharing potentially sensitive data with donors in a particular context. 8",
      "text": "Few donors have formal data sharing policies or guidelines in place.  There is also a lack of shared 7 understanding of terminology and of the objectives and risks around data sharing. There are different definitions and understanding of data-related risks, leading to inconsistent and sometimes contradictory practices around sharing potentially sensitive data with donors in a particular context. 8"
    },
    {
      "self_ref": "#/texts/26",
      "parent": {
        "$ref": "#/groups/4"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 53.858,
            "t": 186.67700000000002,
            "r": 539.349,
            "b": 152.71299999999997,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            434
          ]
        }
      ],
      "orig": "3 Non-personal data is defined as data which was initially personal data, but later made anonymous, such as data about the people affected by the humanitarian situation and their needs, the threats and vulnerabilities they face, and their capacities (adapted from Regulation (EU) 2018/1807 of the European Parliament and of the Council of 14 November 2018 on a framework for the free flow of non-personal data in the European Union ).",
      "text": "3 Non-personal data is defined as data which was initially personal data, but later made anonymous, such as data about the people affected by the humanitarian situation and their needs, the threats and vulnerabilities they face, and their capacities (adapted from Regulation (EU) 2018/1807 of the European Parliament and of the Council of 14 November 2018 on a framework for the free flow of non-personal data in the European Union ).",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/27",
      "parent": {
        "$ref": "#/groups/4"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 53.858,
            "t": 147.67700000000002,
            "r": 501.029,
            "b": 140.71299999999997,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            129
          ]
        }
      ],
      "orig": "4 See the Working Draft OCHA Guidelines for Data Responsibility and the ICRC Handbook on data protection in humanitarian action .",
      "text": "4 See the Working Draft OCHA Guidelines for Data Responsibility and the ICRC Handbook on data protection in humanitarian action .",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/28",
      "parent": {
        "$ref": "#/groups/4"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 53.858,
            "t": 135.67700000000002,
            "r": 273.933,
            "b": 128.71299999999997,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            67
          ]
        }
      ],
      "orig": "5 Read more about the virtual dialogue in this Wilton Park Report .",
      "text": "5 Read more about the virtual dialogue in this Wilton Park Report .",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/29",
      "parent": {
        "$ref": "#/groups/4"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 53.858,
            "t": 123.67700000000002,
            "r": 516.713,
            "b": 107.71299999999997,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            164
          ]
        }
      ],
      "orig": "6 Willits-King, B. and Spencer, A., 2020. Responsible data-sharing with donors: accountability, transparency and data protection in principled humanitarian action .",
      "text": "6 Willits-King, B. and Spencer, A., 2020. Responsible data-sharing with donors: accountability, transparency and data protection in principled humanitarian action .",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/30",
      "parent": {
        "$ref": "#/groups/4"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 53.857,
            "t": 102.67700000000002,
            "r": 536.99,
            "b": 86.71299999999997,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            226
          ]
        }
      ],
      "orig": "7 At the time of writing, only USAID and GIZ had publicly available guidelines on responsible data sharing. See USAID, 2019. Considerations for using data responsibly at USAID and GIZ, 2018. GIZ's Responsible Data Principles .",
      "text": "7 At the time of writing, only USAID and GIZ had publicly available guidelines on responsible data sharing. See USAID, 2019. Considerations for using data responsibly at USAID and GIZ, 2018. GIZ's Responsible Data Principles .",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/31",
      "parent": {
        "$ref": "#/groups/4"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 53.855,
            "t": 81.67700000000002,
            "r": 525.951,
            "b": 65.71299999999997,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            164
          ]
        }
      ],
      "orig": "8 Willits-King, B. and Spencer, A., 2020. Responsible data-sharing with donors: accountability, transparency and data protection in principled humanitarian action .",
      "text": "8 Willits-King, B. and Spencer, A., 2020. Responsible data-sharing with donors: accountability, transparency and data protection in principled humanitarian action .",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/32",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 53.448,
            "t": 47.79200000000003,
            "r": 186.441,
            "b": 40.91399999999999,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            32
          ]
        }
      ],
      "orig": "THE CENTRE FOR HUMANITARIAN DATA",
      "text": "THE CENTRE FOR HUMANITARIAN DATA"
    },
    {
      "self_ref": "#/texts/33",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 269.777,
            "t": 47.75199999999995,
            "r": 324.927,
            "b": 40.874000000000024,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            13
          ]
        }
      ],
      "orig": "DECEMBER 2020",
      "text": "DECEMBER 2020"
    },
    {
      "self_ref": "#/texts/34",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 2,
          "bbox": {
            "l": 537.187,
            "t": 47.60699999999997,
            "r": 541.763,
            "b": 40.418000000000006,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            1
          ]
        }
      ],
      "orig": "2",
      "text": "2"
    },
    {
      "self_ref": "#/texts/35",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.955,
            "t": 793.138,
            "r": 342.344,
            "b": 783.132,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            39
          ]
        }
      ],
      "orig": "OBJECTIVES FOR DATA SHARING WITH DONORS",
      "text": "OBJECTIVES FOR DATA SHARING WITH DONORS",
      "level": 1
    },
    {
      "self_ref": "#/texts/36",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.856,
            "t": 768.817,
            "r": 538.92,
            "b": 732.96,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            219
          ]
        }
      ],
      "orig": "The most commonly identified objectives for donors requesting sensitive data from partners are situational awareness and programme design; accountability and transparency; and legal, regulatory, and policy requirements.",
      "text": "The most commonly identified objectives for donors requesting sensitive data from partners are situational awareness and programme design; accountability and transparency; and legal, regulatory, and policy requirements."
    },
    {
      "self_ref": "#/texts/37",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.856,
            "t": 716.017,
            "r": 280.102,
            "b": 706.446,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            42
          ]
        }
      ],
      "orig": "Situational awareness and programme design",
      "text": "Situational awareness and programme design",
      "level": 1
    },
    {
      "self_ref": "#/texts/38",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.856,
            "t": 702.817,
            "r": 537.369,
            "b": 653.76,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            317
          ]
        }
      ],
      "orig": "Donors seek information and data from humanitarian organizations in order to understand and react to changes in humanitarian contexts. This allows donors to improve their own programme design and evaluation, prevent duplication of assistance, identify information gaps, and ensure appropriate targeting of assistance.",
      "text": "Donors seek information and data from humanitarian organizations in order to understand and react to changes in humanitarian contexts. This allows donors to improve their own programme design and evaluation, prevent duplication of assistance, identify information gaps, and ensure appropriate targeting of assistance."
    },
    {
      "self_ref": "#/texts/39",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.856,
            "t": 636.817,
            "r": 210.858,
            "b": 627.284,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            31
          ]
        }
      ],
      "orig": "Accountability and transparency",
      "text": "Accountability and transparency",
      "level": 1
    },
    {
      "self_ref": "#/texts/40",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.856,
            "t": 623.617,
            "r": 536.401,
            "b": 600.96,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            171
          ]
        }
      ],
      "orig": "Donors and humanitarian organizations have an obligation to account for their activities. Data can enable donors to explain and defend funding on foreign aid to taxpayers.",
      "text": "Donors and humanitarian organizations have an obligation to account for their activities. Data can enable donors to explain and defend funding on foreign aid to taxpayers."
    },
    {
      "self_ref": "#/texts/41",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.856,
            "t": 584.017,
            "r": 259.125,
            "b": 574.484,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            42
          ]
        }
      ],
      "orig": "Legal, regulatory, and policy requirements",
      "text": "Legal, regulatory, and policy requirements",
      "level": 1
    },
    {
      "self_ref": "#/texts/42",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.856,
            "t": 570.817,
            "r": 536.235,
            "b": 495.36,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            578
          ]
        }
      ],
      "orig": "Donors are subject to certain national and international legal requirements, including political, legal and statutory requirements related to counter-terrorism, migration and law enforcement. In many cases, donors might want to use data to verify their compliance with these different requirements. Some donors include counterterrorism clauses in their grant agreements, which are intended to ensure that their funds are not used to benefit designated terrorist groups.  Similarly, donors might include clauses to cover anti9 bribery, anti-fraud and anti-corruption measures. 10",
      "text": "Donors are subject to certain national and international legal requirements, including political, legal and statutory requirements related to counter-terrorism, migration and law enforcement. In many cases, donors might want to use data to verify their compliance with these different requirements. Some donors include counterterrorism clauses in their grant agreements, which are intended to ensure that their funds are not used to benefit designated terrorist groups.  Similarly, donors might include clauses to cover anti9 bribery, anti-fraud and anti-corruption measures. 10"
    },
    {
      "self_ref": "#/texts/43",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.845,
            "t": 466.69,
            "r": 358.278,
            "b": 456.683,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            40
          ]
        }
      ],
      "orig": "CONSTRAINTS FOR DATA SHARING WITH DONORS",
      "text": "CONSTRAINTS FOR DATA SHARING WITH DONORS",
      "level": 1
    },
    {
      "self_ref": "#/texts/44",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.746,
            "t": 442.523,
            "r": 527.732,
            "b": 406.665,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            228
          ]
        }
      ],
      "orig": "Despite these objectives, data sharing with donors is not without its constraints, which include a lack of regulatory frameworks for responsibly managing sensitive non-personal data, capacity gaps and lack of purpose limitation.",
      "text": "Despite these objectives, data sharing with donors is not without its constraints, which include a lack of regulatory frameworks for responsibly managing sensitive non-personal data, capacity gaps and lack of purpose limitation."
    },
    {
      "self_ref": "#/texts/45",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.746,
            "t": 389.723,
            "r": 473.748,
            "b": 380.151,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            82
          ]
        }
      ],
      "orig": "Lack of regulatory frameworks for responsibly managing sensitive non-personal data",
      "text": "Lack of regulatory frameworks for responsibly managing sensitive non-personal data",
      "level": 1
    },
    {
      "self_ref": "#/texts/46",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.746,
            "t": 376.523,
            "r": 543.516,
            "b": 301.06500000000005,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            545
          ]
        }
      ],
      "orig": "The sensitivity of personal data is generally well-known and addressed by a variety of policy and regulatory frameworks, but the same cannot be said for sensitive non-personal data. Protecting groups and their data remains challenging due to the current gaps in regulation and guidance and the overall lack of understanding regarding the sensitivity of non-personal data. These data policy gaps increase the risk of sensitive data not being stored or protected adequately or shared inadvertently by partners in order to satisfy donors' requests.",
      "text": "The sensitivity of personal data is generally well-known and addressed by a variety of policy and regulatory frameworks, but the same cannot be said for sensitive non-personal data. Protecting groups and their data remains challenging due to the current gaps in regulation and guidance and the overall lack of understanding regarding the sensitivity of non-personal data. These data policy gaps increase the risk of sensitive data not being stored or protected adequately or shared inadvertently by partners in order to satisfy donors' requests."
    },
    {
      "self_ref": "#/texts/47",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.746,
            "t": 284.12300000000005,
            "r": 120.823,
            "b": 274.58899999999994,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            13
          ]
        }
      ],
      "orig": "Capacity gaps",
      "text": "Capacity gaps",
      "level": 1
    },
    {
      "self_ref": "#/texts/48",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.746,
            "t": 270.923,
            "r": 535.014,
            "b": 195.461,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            552
          ]
        }
      ],
      "orig": "Responding to ad-hoc data sharing requests from donors can be viewed as an additional burden to humanitarian responders, diverting critical time, resources and focus away from other implementing activities. 11 Insufficient funding for data-related capacity development has limited many organizations' ability to provide their staff with the skills and resources required for managing data responsibly. 12 Gaps in capacity to fulfil donor requirements might also deter smaller and/or local NGOs from seeking funding, undermining localization efforts. 13",
      "text": "Responding to ad-hoc data sharing requests from donors can be viewed as an additional burden to humanitarian responders, diverting critical time, resources and focus away from other implementing activities. 11 Insufficient funding for data-related capacity development has limited many organizations' ability to provide their staff with the skills and resources required for managing data responsibly. 12 Gaps in capacity to fulfil donor requirements might also deter smaller and/or local NGOs from seeking funding, undermining localization efforts. 13"
    },
    {
      "self_ref": "#/texts/49",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "footnote",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.858,
            "t": 163.11799999999994,
            "r": 303.061,
            "b": 156.154,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            73
          ]
        }
      ],
      "orig": "9 See NRC's Toolkit for Principled Humanitarian Action; Managing CT Risks",
      "text": "9 See NRC's Toolkit for Principled Humanitarian Action; Managing CT Risks"
    },
    {
      "self_ref": "#/texts/50",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 303.061,
            "t": 162.625,
            "r": 304.426,
            "b": 156.20100000000002,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            1
          ]
        }
      ],
      "orig": ".",
      "text": "."
    },
    {
      "self_ref": "#/texts/51",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "footnote",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.858,
            "t": 151.11799999999994,
            "r": 542.854,
            "b": 99.154,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            742
          ]
        }
      ],
      "orig": "10 In order to ensure compliance, donors might request highly disaggregated data to corroborate their due diligence processes, ensuring their partners are not engaging with any 'sanctioned' person or entity'. See Walker, J., 2020. Compliance Dialogue on Syria-Related Humanitarian Payments . 'Sanctioned persons' is a general term which may include individuals, terrorist groups, governments as well as companies and other entities of legal personality. The EU, for example, has over the years considerably strengthened its legal framework for preventing money laundering and terrorism financing in recent years and is constantly enforcing in. See: NGO Voice, 2020 . The Impact of EU Sanctions and Restrictive Measures on Humanitarian Action.",
      "text": "10 In order to ensure compliance, donors might request highly disaggregated data to corroborate their due diligence processes, ensuring their partners are not engaging with any 'sanctioned' person or entity'. See Walker, J., 2020. Compliance Dialogue on Syria-Related Humanitarian Payments . 'Sanctioned persons' is a general term which may include individuals, terrorist groups, governments as well as companies and other entities of legal personality. The EU, for example, has over the years considerably strengthened its legal framework for preventing money laundering and terrorism financing in recent years and is constantly enforcing in. See: NGO Voice, 2020 . The Impact of EU Sanctions and Restrictive Measures on Humanitarian Action."
    },
    {
      "self_ref": "#/texts/52",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "footnote",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.855,
            "t": 94.11799999999994,
            "r": 506.372,
            "b": 78.154,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            156
          ]
        }
      ],
      "orig": "11 Inter-Agency Standing Committee (IASC) Humanitarian Financing Task Team (HFTT), 2016. Donor Conditions and their implications for humanitarian response .",
      "text": "11 Inter-Agency Standing Committee (IASC) Humanitarian Financing Task Team (HFTT), 2016. Donor Conditions and their implications for humanitarian response ."
    },
    {
      "self_ref": "#/texts/53",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "footnote",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.858,
            "t": 73.11799999999994,
            "r": 336.451,
            "b": 66.154,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            85
          ]
        }
      ],
      "orig": "12 Publish What You Fund, 2020. Data Use Capacity in Protracted Humanitarian Crises .",
      "text": "12 Publish What You Fund, 2020. Data Use Capacity in Protracted Humanitarian Crises ."
    },
    {
      "self_ref": "#/texts/54",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 53.448,
            "t": 47.79200000000003,
            "r": 186.441,
            "b": 40.91399999999999,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            32
          ]
        }
      ],
      "orig": "THE CENTRE FOR HUMANITARIAN DATA",
      "text": "THE CENTRE FOR HUMANITARIAN DATA"
    },
    {
      "self_ref": "#/texts/55",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 269.777,
            "t": 47.75199999999995,
            "r": 324.927,
            "b": 40.874000000000024,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            13
          ]
        }
      ],
      "orig": "DECEMBER 2020",
      "text": "DECEMBER 2020"
    },
    {
      "self_ref": "#/texts/56",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 3,
          "bbox": {
            "l": 537.187,
            "t": 47.60699999999997,
            "r": 541.763,
            "b": 40.418000000000006,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            1
          ]
        }
      ],
      "orig": "3",
      "text": "3"
    },
    {
      "self_ref": "#/texts/57",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 53.022,
            "t": 792.801,
            "r": 143.209,
            "b": 783.268,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            18
          ]
        }
      ],
      "orig": "Purpose limitation",
      "text": "Purpose limitation",
      "level": 1
    },
    {
      "self_ref": "#/texts/58",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 53.022,
            "t": 779.601,
            "r": 538.613,
            "b": 690.948,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            715
          ]
        }
      ],
      "orig": "The principle of purpose limitation requires that data is only collected for specified, explicit and legitimate purposes, and that it not be processed further in a manner that would be incompatible with those purposes. 14 Even when donors specify legitimate reasons for requesting data in-line with the original purposes for which the data was collected (e.g. the delivery of humanitarian assistance), it can be difficult to ensure that the data will not be used for other purposes once shared. Data used out of context and for purposes that are not known at the time of sharing, or retained past the intended retention for a defined purpose represents a violation, even if unintended, of the data subjects' rights.",
      "text": "The principle of purpose limitation requires that data is only collected for specified, explicit and legitimate purposes, and that it not be processed further in a manner that would be incompatible with those purposes. 14 Even when donors specify legitimate reasons for requesting data in-line with the original purposes for which the data was collected (e.g. the delivery of humanitarian assistance), it can be difficult to ensure that the data will not be used for other purposes once shared. Data used out of context and for purposes that are not known at the time of sharing, or retained past the intended retention for a defined purpose represents a violation, even if unintended, of the data subjects' rights."
    },
    {
      "self_ref": "#/texts/59",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 54.102,
            "t": 662.389,
            "r": 180.183,
            "b": 652.382,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            15
          ]
        }
      ],
      "orig": "RECOMMENDATIONS",
      "text": "RECOMMENDATIONS",
      "level": 1
    },
    {
      "self_ref": "#/texts/60",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 54.025,
            "t": 638.222,
            "r": 537.78,
            "b": 589.164,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            357
          ]
        }
      ],
      "orig": "In view of the objectives and constraints detailed above, the Centre, the Humanitarian Policy Group (HPG) at ODI, the ICRC, and the Human Security Division of the Swiss Federal Department of Foreign Affairs recommend that donors and humanitarian organizations take the following steps to minimize risks while maximizing benefits when sharing sensitive data:",
      "text": "In view of the objectives and constraints detailed above, the Centre, the Humanitarian Policy Group (HPG) at ODI, the ICRC, and the Human Security Division of the Swiss Federal Department of Foreign Affairs recommend that donors and humanitarian organizations take the following steps to minimize risks while maximizing benefits when sharing sensitive data:"
    },
    {
      "self_ref": "#/texts/61",
      "parent": {
        "$ref": "#/groups/5"
      },
      "children": [],
      "content_layer": "body",
      "label": "list_item",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 65.366,
            "t": 572.222,
            "r": 516.009,
            "b": 549.488,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            121
          ]
        }
      ],
      "orig": "· Reviewing and clarifying the formal or informal frameworks that govern the collection and sharing of disaggregated data",
      "text": "· Reviewing and clarifying the formal or informal frameworks that govern the collection and sharing of disaggregated data",
      "enumerated": false,
      "marker": "-"
    },
    {
      "self_ref": "#/texts/62",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 76.707,
            "t": 545.822,
            "r": 543.16,
            "b": 483.564,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            415
          ]
        }
      ],
      "orig": "Donors and partners should examine the official, formal requirements and ad-hoc, informal requirements of data sharing, and analyse partner and donor staff interpret whether requirements correctly and consistently. They should assess whether there are implicit conditionalities between the willingness to share disaggregated data and the ability of different organizations to access and sustain funding from donors.",
      "text": "Donors and partners should examine the official, formal requirements and ad-hoc, informal requirements of data sharing, and analyse partner and donor staff interpret whether requirements correctly and consistently. They should assess whether there are implicit conditionalities between the willingness to share disaggregated data and the ability of different organizations to access and sustain funding from donors."
    },
    {
      "self_ref": "#/texts/63",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 65.366,
            "t": 466.622,
            "r": 353.761,
            "b": 457.088,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            59
          ]
        }
      ],
      "orig": "· Formalizing and standardizing requests for sensitive data",
      "text": "· Formalizing and standardizing requests for sensitive data",
      "level": 1
    },
    {
      "self_ref": "#/texts/64",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 76.707,
            "t": 453.422,
            "r": 535.184,
            "b": 377.964,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            576
          ]
        }
      ],
      "orig": "When sensitive data is required to meet a mutually agreed objective, donors should formalize and standardize their requests for such data. Requests should be made in writing and should specify which data is requested, the format desired, and the intended use of the data. Donors should only request the information required to meet the specified purpose for which it is being requested and should indicate a timeline for destruction of the data. Humanitarian organisations should document all requests for data and ensure consistency in responding to these requests over time.",
      "text": "When sensitive data is required to meet a mutually agreed objective, donors should formalize and standardize their requests for such data. Requests should be made in writing and should specify which data is requested, the format desired, and the intended use of the data. Donors should only request the information required to meet the specified purpose for which it is being requested and should indicate a timeline for destruction of the data. Humanitarian organisations should document all requests for data and ensure consistency in responding to these requests over time."
    },
    {
      "self_ref": "#/texts/65",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 65.366,
            "t": 361.022,
            "r": 399.521,
            "b": 351.488,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            68
          ]
        }
      ],
      "orig": "· Investing in data management capacities of staff and organizations",
      "text": "· Investing in data management capacities of staff and organizations",
      "level": 1
    },
    {
      "self_ref": "#/texts/66",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 76.707,
            "t": 347.822,
            "r": 544.724,
            "b": 311.96399999999994,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            299
          ]
        }
      ],
      "orig": "Donors and humanitarian organizations should identify opportunities to invest in building data management expertise especially for non-technical staff. The donor community is uniquely positioned to encourage data responsibility by  providing additional  resources for training and capacity building.",
      "text": "Donors and humanitarian organizations should identify opportunities to invest in building data management expertise especially for non-technical staff. The donor community is uniquely positioned to encourage data responsibility by  providing additional  resources for training and capacity building."
    },
    {
      "self_ref": "#/texts/67",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "section_header",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 65.366,
            "t": 295.02199999999993,
            "r": 353.751,
            "b": 285.48800000000006,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            54
          ]
        }
      ],
      "orig": "· Adopting common principles for donor data management",
      "text": "· Adopting common principles for donor data management",
      "level": 1
    },
    {
      "self_ref": "#/texts/68",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 76.705,
            "t": 281.822,
            "r": 543.102,
            "b": 206.361,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            551
          ]
        }
      ],
      "orig": "The sector already has a range of principles and commitments to inform different aspects of humanitarian donorship. 15  However, these do not sufficiently address concerns related to data responsibility. Donors and partners should engage in the development of common principles and guidelines for donor data sharing to fill this gap. The Humanitarian Data and Trust Initiative , co-led by the Government of Switzerland, the ICRC, and the Centre, offers a platform to facilitate this process as part of its ongoing work to build trust through dialogue.",
      "text": "The sector already has a range of principles and commitments to inform different aspects of humanitarian donorship. 15  However, these do not sufficiently address concerns related to data responsibility. Donors and partners should engage in the development of common principles and guidelines for donor data sharing to fill this gap. The Humanitarian Data and Trust Initiative , co-led by the Government of Switzerland, the ICRC, and the Centre, offers a platform to facilitate this process as part of its ongoing work to build trust through dialogue."
    },
    {
      "self_ref": "#/texts/69",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 54.023,
            "t": 189.418,
            "r": 531.221,
            "b": 166.71900000000005,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            159
          ]
        }
      ],
      "orig": "Organizations are encouraged to share their experience in responsible data sharing with donors with the Centre for Humanitarian Data via centrehumdata@un.org .",
      "text": "Organizations are encouraged to share their experience in responsible data sharing with donors with the Centre for Humanitarian Data via centrehumdata@un.org ."
    },
    {
      "self_ref": "#/texts/70",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "footnote",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 53.858,
            "t": 84.46500000000003,
            "r": 276.104,
            "b": 77.50099999999998,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            67
          ]
        }
      ],
      "orig": "14 ICRC, 2020. Handbook on data protection in humanitarian action .",
      "text": "14 ICRC, 2020. Handbook on data protection in humanitarian action ."
    },
    {
      "self_ref": "#/texts/71",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "footnote",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 53.858,
            "t": 72.46500000000003,
            "r": 344.138,
            "b": 65.50099999999998,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            86
          ]
        }
      ],
      "orig": "15 Examples include the Good Humanitarian Donorship Initiative and the Grand Bargain .",
      "text": "15 Examples include the Good Humanitarian Donorship Initiative and the Grand Bargain ."
    },
    {
      "self_ref": "#/texts/72",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 53.448,
            "t": 47.79200000000003,
            "r": 186.441,
            "b": 40.91399999999999,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            32
          ]
        }
      ],
      "orig": "THE CENTRE FOR HUMANITARIAN DATA",
      "text": "THE CENTRE FOR HUMANITARIAN DATA"
    },
    {
      "self_ref": "#/texts/73",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 269.777,
            "t": 47.75199999999995,
            "r": 324.927,
            "b": 40.874000000000024,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            13
          ]
        }
      ],
      "orig": "DECEMBER 2020",
      "text": "DECEMBER 2020"
    },
    {
      "self_ref": "#/texts/74",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 4,
          "bbox": {
            "l": 537.187,
            "t": 47.60699999999997,
            "r": 541.763,
            "b": 40.418000000000006,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            1
          ]
        }
      ],
      "orig": "4",
      "text": "4"
    },
    {
      "self_ref": "#/texts/75",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 53.394,
            "t": 294.47,
            "r": 530.901,
            "b": 273.83500000000004,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            172
          ]
        }
      ],
      "orig": "COLLABORATORS: THE HUMANITARIAN POLICY GROUP AT ODI; INTERNATIONAL COMMITTEE OF THE RED CROSS; AND THE HUMAN SECURITY DIVISION, SWISS FEDERAL DEPARTMENT OF FOREIGN AFFAIRS.",
      "text": "COLLABORATORS: THE HUMANITARIAN POLICY GROUP AT ODI; INTERNATIONAL COMMITTEE OF THE RED CROSS; AND THE HUMAN SECURITY DIVISION, SWISS FEDERAL DEPARTMENT OF FOREIGN AFFAIRS."
    },
    {
      "self_ref": "#/texts/76",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 65.224,
            "t": 251.91100000000006,
            "r": 524.506,
            "b": 183.313,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            609
          ]
        }
      ],
      "orig": "The Centre for Humanitarian Data ('the Center'), together with key partners, is publishing a series of eight guidance notes on Data Responsibility in Humanitarian Action over the course of 2019 and 2020. The Guidance Note series follows the publication of the OCHA Data Responsibility Guidelines in March 2019. Through the series, the Centre aims to provide additional guidance on specific issues, processes and tools for data responsibility in practice. This series is made possible with the generous support of the Directorate-General for European Civil Protection and Humanitarian Aid Operations (DG ECHO).",
      "text": "The Centre for Humanitarian Data ('the Center'), together with key partners, is publishing a series of eight guidance notes on Data Responsibility in Humanitarian Action over the course of 2019 and 2020. The Guidance Note series follows the publication of the OCHA Data Responsibility Guidelines in March 2019. Through the series, the Centre aims to provide additional guidance on specific issues, processes and tools for data responsibility in practice. This series is made possible with the generous support of the Directorate-General for European Civil Protection and Humanitarian Aid Operations (DG ECHO)."
    },
    {
      "self_ref": "#/texts/77",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 145.488,
            "t": 155.69000000000005,
            "r": 543.907,
            "b": 115.55200000000002,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            336
          ]
        }
      ],
      "orig": "This document covers humanitarian aid activities implemented with the financial assistance of the European Union. The views expressed herein should not be taken, in any way, to reflect the official opinion of the European Union, and the European Commission is not responsible for any use that may be made of the information it contains.",
      "text": "This document covers humanitarian aid activities implemented with the financial assistance of the European Union. The views expressed herein should not be taken, in any way, to reflect the official opinion of the European Union, and the European Commission is not responsible for any use that may be made of the information it contains."
    },
    {
      "self_ref": "#/texts/78",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "text",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 53.953,
            "t": 96.57100000000003,
            "r": 136.381,
            "b": 80.81399999999996,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            47
          ]
        }
      ],
      "orig": "This project is co-funded by the European Union",
      "text": "This project is co-funded by the European Union"
    },
    {
      "self_ref": "#/texts/79",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 53.448,
            "t": 47.79200000000003,
            "r": 186.441,
            "b": 40.91399999999999,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            32
          ]
        }
      ],
      "orig": "THE CENTRE FOR HUMANITARIAN DATA",
      "text": "THE CENTRE FOR HUMANITARIAN DATA"
    },
    {
      "self_ref": "#/texts/80",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 269.777,
            "t": 47.75199999999995,
            "r": 324.927,
            "b": 40.874000000000024,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            13
          ]
        }
      ],
      "orig": "DECEMBER 2020",
      "text": "DECEMBER 2020"
    },
    {
      "self_ref": "#/texts/81",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "furniture",
      "label": "page_footer",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 537.187,
            "t": 47.60699999999997,
            "r": 541.763,
            "b": 40.418000000000006,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            1
          ]
        }
      ],
      "orig": "5",
      "text": "5"
    }
  ],
  "pictures": [
    {
      "self_ref": "#/pictures/0",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "picture",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 53.23921203613281,
            "t": 812.4467735290527,
            "r": 189.67942810058594,
            "b": 792.1901092529297,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            0
          ]
        }
      ],
      "captions": [],
      "references": [],
      "footnotes": [],
      "annotations": []
    },
    {
      "self_ref": "#/pictures/1",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "picture",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 314.2784729003906,
            "t": 841.8900146484375,
            "r": 437.1101989746094,
            "b": 771.4219512939453,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            0
          ]
        }
      ],
      "captions": [],
      "references": [],
      "footnotes": [],
      "annotations": []
    },
    {
      "self_ref": "#/pictures/2",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "picture",
      "prov": [
        {
          "page_no": 1,
          "bbox": {
            "l": 469.7768249511719,
            "t": 841.5787353515625,
            "r": 592.5189819335938,
            "b": 701.9815216064453,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            0
          ]
        }
      ],
      "captions": [],
      "references": [],
      "footnotes": [],
      "annotations": []
    },
    {
      "self_ref": "#/pictures/3",
      "parent": {
        "$ref": "#/body"
      },
      "children": [],
      "content_layer": "body",
      "label": "picture",
      "prov": [
        {
          "page_no": 5,
          "bbox": {
            "l": 52.50861740112305,
            "t": 158.22454833984375,
            "r": 134.75924682617188,
            "b": 102.72418212890625,
            "coord_origin": "BOTTOMLEFT"
          },
          "charspan": [
            0,
            0
          ]
        }
      ],
      "captions": [],
      "references": [],
      "footnotes": [],
      "annotations": []
    }
  ],
  "tables": [],
  "key_value_items": [],
  "form_items": [],
  "pages": {
    "1": {
      "size": {
        "width": 595.2760009765625,
        "height": 841.8900146484375
      },
      "page_no": 1
    },
    "2": {
      "size": {
        "width": 595.2760009765625,
        "height": 841.8900146484375
      },
      "page_no": 2
    },
    "3": {
      "size": {
        "width": 595.2760009765625,
        "height": 841.8900146484375
      },
      "page_no": 3
    },
    "4": {
      "size": {
        "width": 595.2760009765625,
        "height": 841.8900146484375
      },
      "page_no": 4
    },
    "5": {
      "size": {
        "width": 595.2760009765625,
        "height": 841.8900146484375
      },
      "page_no": 5
    }
  }
}""
Your long input text goes here.
It can be multiple paragraphs, tables, or any content you want to test.
"""

chunks = chunk_text_with_strategy(input_text, strategy="recursive")

for i, chunk in enumerate(chunks, 1):
    print(f"--- Chunk {i} ---")
    print(chunk)
    print()
