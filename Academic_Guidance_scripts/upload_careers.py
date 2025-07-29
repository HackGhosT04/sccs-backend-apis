import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

 

# Your original nested dict (as you posted)
UMP_COURSES = {
    "Faculty of Agriculture and Natural Sciences": {
        "School of Agricultural Sciences": {
            "undergraduate": [
                {
                    "name": "Diploma in Agriculture in Plant Production",
                    "related_interests": ["Science", "Business"]
                },
                {
                    "name": "Diploma in Animal Production",
                    "related_interests": ["Science", "Business"]
                },
                {
                    "name": "Bachelor of Agriculture in Agricultural Extension and Rural Resource Management",
                    "related_interests": ["Science", "Education", "Business"]
                },
                {
                    "name": "Bachelor of Science in Agriculture",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Science in Forestry",
                    "related_interests": ["Science"]
                }
            ],
            "postgraduate": [
                {
                    "name": "Advanced Diploma in Agriculture in Agricultural Extension",
                    "related_interests": ["Science", "Education", "Business"]
                },
                {
                    "name": "Advanced Diploma in Agriculture in Agricultural Production Management",
                    "related_interests": ["Science", "Business"]
                },
                {
                    "name": "Advanced Diploma in Agriculture in Post Harvest Technology",
                    "related_interests": ["Science", "Business"]
                },
                {
                    "name": "Advanced Diploma in Animal Production",
                    "related_interests": ["Science", "Business"]
                },
                {
                    "name": "Postgraduate Diploma in Agriculture",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Agriculture Honours in Agricultural Extension and Rural Resource Management",
                    "related_interests": ["Science", "Education", "Business"]
                },
                {
                    "name": "Master of Science in Agriculture",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Master of Agriculture in Agricultural Extension",
                    "related_interests": ["Science", "Education", "Business"]
                },
                {
                    "name": "Doctor of Philosophy (PhD) in Agriculture",
                    "related_interests": ["Science"]
                }
            ]
        },
        "School of Biology and Environmental Sciences": {
            "undergraduate": [
                {
                    "name": "Diploma in Nature Conservation",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Science",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Science in Environmental Science",
                    "related_interests": ["Science"]
                }
            ],
            "postgraduate": [
                {
                    "name": "Advanced Diploma in Nature Conservation",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Arts Honours in Geography",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Science Honours in Ecology",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Science Honours in Entomology",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Bachelor of Science Honours in Geography",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Postgraduate Diploma in Nature Conservation",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Master of Science",
                    "related_interests": ["Science"]
                },
                {
                    "name": "Doctor of Philosophy (PhD) (General)",
                    "related_interests": ["Science"]
                }
            ]
        },
        "School of Computing and Mathematical Sciences": {
            "undergraduate": [
                {
                    "name": "Higher Certificate in Information Communication Technology in User Support",
                    "related_interests": ["Technology"]
                },
                {
                    "name": "Diploma in Information and Communication Technology in Applications Development",
                    "related_interests": ["Technology", "Art & Design"]
                },
                {
                    "name": "Bachelor of Information and Communication Technology",
                    "related_interests": ["Technology", "Business"]
                }
            ],
            "postgraduate": [
                {
                    "name": "Advanced Diploma in Information and Communication Technology in Applications Development",
                    "related_interests": ["Technology", "Art & Design"]
                },
                {
                    "name": "Postgraduate Diploma in Information and Communication Technology",
                    "related_interests": ["Technology", "Business"]
                },
                {
                    "name": "Master of Computing",
                    "related_interests": ["Technology"]
                }
            ]
        }
    },
    "Faculty of Education": {
        "School of Early Childhood Education": {
            "undergraduate": [
                {
                    "name": "Bachelor of Education in Foundation Phase Teaching",
                    "related_interests": ["Education"]
                }
            ],
            "postgraduate": [
                {
                    "name": "Bachelor of Education in Teaching & Learning (Honours)",
                    "related_interests": ["Education"]
                },
                {
                    "name": "Master of Education in Early Childhood Education",
                    "related_interests": ["Education"]
                },
                {
                    "name": "Doctor of Philosophy in Education",
                    "related_interests": ["Education"]
                }
            ]
        }
    },
    "Faculty of Economics, Development and Business Sciences": {
        "School of Development Studies": {
            "undergraduate": [
                {
                    "name": "Bachelor of Commerce (General)",
                    "related_interests": ["Business", "Finance"]
                },
                {
                    "name": "Bachelor of Development Studies",
                    "related_interests": ["Business", "Education"]
                },
                {
                    "name": "Bachelor of Administration",
                    "related_interests": ["Business"]
                },
                {
                    "name": "Bachelor of Laws",
                    "related_interests": ["Law"]
                }
            ],
            "postgraduate": [
                {
                    "name": "Bachelor of Administration Honours",
                    "related_interests": ["Business"]
                },
                {
                    "name": "Bachelor of Commerce Honours in Economics",
                    "related_interests": ["Business", "Finance"]
                },
                {
                    "name": "Bachelor of Development Studies Honours",
                    "related_interests": ["Business", "Education"]
                },
                {
                    "name": "Master of Administration (MAdmin)",
                    "related_interests": ["Business"]
                },
                {
                    "name": "Master of Commerce (MCom)",
                    "related_interests": ["Business", "Finance"]
                },
                {
                    "name": "Master of Commerce in Business Management",
                    "related_interests": ["Business"]
                },
                {
                    "name": "Master of Development Studies",
                    "related_interests": ["Business", "Education"]
                },
                {
                    "name": "Doctor of Philosophy in Development Studies",
                    "related_interests": ["Business", "Education"]
                },
                {
                    "name": "Doctor of Philosophy in Economics",
                    "related_interests": ["Business", "Finance"]
                }
            ]
        },
        "School of Hospitality and Tourism Management": {
            "undergraduate": [
                {
                    "name": "Diploma in Hospitality Management",
                    "related_interests": ["Business", "Marketing"]
                },
                {
                    "name": "Higher Certificate in Event Management",
                    "related_interests": ["Business", "Marketing", "Art & Design"]
                },
                {
                    "name": "Diploma in Culinary Arts",
                    "related_interests": ["Art & Design", "Business"]
                },
                {
                    "name": "Diploma in Hospitality Management (Revised Curriculum)",
                    "related_interests": ["Business", "Marketing"]
                }
            ],
            "postgraduate": [
                {
                    "name": "Advanced Diploma in Hospitality Management",
                    "related_interests": ["Business", "Marketing"]
                },
                {
                    "name": "Postgraduate Diploma in Hospitality Management",
                    "related_interests": ["Business", "Marketing"]
                },
                {
                    "name": "Bachelor of Arts Honours in Tourism",
                    "related_interests": ["Business", "Marketing", "Art & Design"]
                },
                {
                    "name": "Master of Tourism and Hospitality Management",
                    "related_interests": ["Business", "Marketing"]
                }
            ]
        },
        "School of Social Sciences": {
            "undergraduate": [
                {
                    "name": "Bachelor of Arts (General)",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Bachelor of Arts in Media, Communication and Culture",
                    "related_interests": ["Art & Design", "Marketing"]
                },
                {
                    "name": "Bachelor of Social Work",
                    "related_interests": ["Healthcare", "Education"]
                }
            ],
            "postgraduate": [
                {
                    "name": "Bachelor of Arts Honours in Political Science",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Bachelor of Arts Honours in isiNdebele",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Bachelor of Arts Honours in Culture and Heritage Studies",
                    "related_interests": ["Art & Design"]
                },
                {
                    "name": "Bachelor of Arts Honours in Archaeology",
                    "related_interests": ["Art & Design"]
                },
                {
                    "name": "Bachelor of Arts Honours in English",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Bachelor of Arts Honours in Sociology",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Bachelor of Arts Honours in Psychology",
                    "related_interests": ["Healthcare", "Education"]
                },
                {
                    "name": "Bachelor of Arts Honours in Siswati",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Bachelor of Arts Honours in Gender Studies",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Master of Arts in Psychology",
                    "related_interests": ["Healthcare", "Education"]
                },
                {
                    "name": "Master of Arts in Siswati",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Master of Arts in English",
                    "related_interests": ["Art & Design", "Education"]
                },
                {
                    "name": "Master of Arts in Sociology",
                    "related_interests": ["Art & Design", "Education"]
                }
            ]
        }
    }
}
 
careers = [
    {
        "id": "plant_production_technician",
        "title": "Plant Production Technician",
        "description": "Supports and implements crop production practices, from planting through harvest.",
        "skills": [
            "Crop management",
            "Soil analysis",
            "Pest and disease identification",
            "Irrigation planning",
            "Record keeping"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Introduction to Plant Science",
                    "Soil Science Basics",
                    "Principles of Agronomy",
                    "Farm Safety and Hygiene"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Crop Physiology",
                    "Integrated Pest Management",
                    "Farm Machinery Operations",
                    "Data Recording & Analysis"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Protected Cultivation",
                    "Precision Agriculture Tools",
                    "Post‑Harvest Handling",
                    "Sustainable Practices"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Farm Management",
                    "Extension Methods",
                    "Entrepreneurship in Agriculture",
                    "Internship / Work Placement"
                ]
            }
        ],
        "related_interests": ["Science", "Business"]
    },
    {
        "id": "animal_production_technician",
        "title": "Animal Production Technician",
        "description": "Manages day‑to‑day operations in livestock production and animal health monitoring.",
        "skills": [
            "Animal husbandry",
            "Nutrition planning",
            "Herd health monitoring",
            "Breeding management",
            "Data collection"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Animal Science",
                    "Animal Anatomy & Physiology",
                    "Feed & Nutrition Fundamentals",
                    "Veterinary First Aid"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Livestock Production Systems",
                    "Reproductive Management",
                    "Disease Prevention",
                    "Animal Welfare Practices"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Genetics & Breeding",
                    "Advanced Nutrition Formulation",
                    "Farm Business Management",
                    "Quality Assurance"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Extension & Advisory Services",
                    "Entrepreneurship in Animal Production",
                    "Research Methods",
                    "Work Integrated Learning"
                ]
            }
        ],
        "related_interests": ["Science", "Business"]
    },
    {
        "id": "agricultural_extension_officer",
        "title": "Agricultural Extension Officer",
        "description": "Bridges between research and farmers, delivering new technologies and best practices.",
        "skills": [
            "Communication",
            "Training & facilitation",
            "Needs assessment",
            "Project planning",
            "Monitoring & evaluation"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Principles of Rural Development",
                    "Fundamentals of Communication",
                    "Intro to Agricultural Systems",
                    "Ethics and Professionalism"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Adult Learning Techniques",
                    "Community Mobilization",
                    "Participatory Methods",
                    "Statistical Methods"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Extension Program Design",
                    "Impact Assessment",
                    "Policy & Advocacy",
                    "Innovations in Agriculture"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Leadership in Extension",
                    "Entrepreneurship & Value Chains",
                    "Capstone Project",
                    "Field Attachment"
                ]
            }
        ],
        "related_interests": ["Science", "Education", "Business"]
    },
    {
        "id": "agricultural_scientist",
        "title": "Agricultural Scientist",
        "description": "Conducts research to improve crop yields, sustainability and food security.",
        "skills": [
            "Experimental design",
            "Lab techniques",
            "Statistical analysis",
            "Scientific writing",
            "Project management"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Biology for Agriculture",
                    "Chemistry Basics",
                    "Intro to Research Methods",
                    "Data & Statistics I"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Plant Genetics",
                    "Soil Chemistry",
                    "Data & Statistics II",
                    "Scientific Communication"
                ]
            },
            {
                "title": "Specialization",
                "year": "Year 3",
                "courses": [
                    "Crop Improvement Techniques",
                    "Biotechnology Applications",
                    "Field Experimentation",
                    "Ethics in Research"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Advanced Research Project",
                    "Grant Writing & Funding",
                    "Research Dissemination",
                    "Industry Internship"
                ]
            }
        ],
        "related_interests": ["Science"]
    },
    {
        "id": "forester",
        "title": "Forester",
        "description": "Manages forests for timber production, conservation and ecological services.",
        "skills": [
            "Forest inventory",
            "GIS mapping",
            "Silviculture",
            "Environmental assessment",
            "Resource management"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Forestry",
                    "Ecology Fundamentals",
                    "Basic Cartography",
                    "Forest Biology"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Forest Ecology",
                    "Silvicultural Systems",
                    "GIS for Natural Resources",
                    "Forest Health"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Forest Mensuration",
                    "Harvest Planning",
                    "Restoration Ecology",
                    "Wildlife Management"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Forest Policy & Law",
                    "Sustainable Resource Management",
                    "Industry Placement",
                    "Capstone Project"
                ]
            }
        ],
        "related_interests": ["Science"]
    },
    {
        "id": "conservation_technician",
        "title": "Conservation Technician",
        "description": "Maintains and monitors protected areas, wildlife habitats and biodiversity projects.",
        "skills": [
            "Species identification",
            "Habitat assessment",
            "Patrol and enforcement",
            "Data collection",
            "Community engagement"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Conservation",
                    "Basic Ecology",
                    "Fieldwork Techniques",
                    "GIS Basics"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Wildlife Management",
                    "Protected Area Management",
                    "Monitoring & Evaluation",
                    "Environmental Education"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Human‑Wildlife Conflict",
                    "Conservation Law",
                    "Community‑Based Projects",
                    "Research Methods"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Internship in Conservation",
                    "Project Planning",
                    "Grant Writing",
                    "Capstone Field Study"
                ]
            }
        ],
        "related_interests": ["Science"]
    },
    {
        "id": "environmental_scientist",
        "title": "Environmental Scientist",
        "description": "Assesses and addresses environmental issues across air, water and soil systems.",
        "skills": [
            "Sampling and analysis",
            "Environmental impact assessment",
            "Regulatory compliance",
            "Report writing",
            "GIS and remote sensing"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Environmental Science",
                    "Chemistry for the Environment",
                    "Field Methods I",
                    "Data Analysis I"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Environmental Chemistry",
                    "Water Resource Management",
                    "Air Quality Monitoring",
                    "Data Analysis II"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Impact Assessment",
                    "Waste Management",
                    "GIS Applications",
                    "Policy & Regulation"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Project",
                    "Professional Ethics",
                    "Industry Placement",
                    "Communication & Outreach"
                ]
            }
        ],
        "related_interests": ["Science"]
    },
    {
        "id": "ict_support_specialist",
        "title": "ICT Support Specialist",
        "description": "Provides technical assistance and troubleshooting for end‑users and networks.",
        "skills": [
            "Hardware diagnostics",
            "Operating systems",
            "Customer service",
            "Network basics",
            "Documentation"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to ICT",
                    "Operating Systems I",
                    "Computer Hardware Essentials",
                    "Helpdesk Fundamentals"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Networking Basics",
                    "Operating Systems II",
                    "Scripting for Support",
                    "ITIL Foundations"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Network Administration",
                    "Security Fundamentals",
                    "Virtualization",
                    "Service Management"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Support Project",
                    "Advanced Troubleshooting",
                    "Internship",
                    "Professional Certification Prep"
                ]
            }
        ],
        "related_interests": ["Technology"]
    },
    {
        "id": "applications_developer",
        "title": "Applications Developer",
        "description": "Designs and builds custom software applications for business needs.",
        "skills": [
            "Programming",
            "Database design",
            "Debugging",
            "User interface design",
            "Version control"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Programming Fundamentals",
                    "Database Concepts",
                    "Web Technologies I",
                    "Software Engineering Basics"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Object‑Oriented Programming",
                    "Database Systems",
                    "Web Technologies II",
                    "Software Testing"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Mobile App Development",
                    "API Design",
                    "DevOps Essentials",
                    "UI/UX Principles"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Development Project",
                    "Agile Methods",
                    "Internship",
                    "Portfolio Review"
                ]
            }
        ],
        "related_interests": ["Technology", "Art & Design", "Business"]
    },
    {
        "id": "systems_analyst",
        "title": "Systems Analyst",
        "description": "Analyzes business requirements to design and improve IT systems.",
        "skills": [
            "Requirements gathering",
            "Process modeling",
            "Data analysis",
            "Communication",
            "Project planning"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to ICT",
                    "Business Communication",
                    "Data Analysis I",
                    "Systems Concepts"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Database Systems",
                    "Business Process Modeling",
                    "Data Analysis II",
                    "Software Engineering"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Requirements Engineering",
                    "Project Management",
                    "IT Governance",
                    "Change Management"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Analysis Project",
                    "Stakeholder Engagement",
                    "Internship",
                    "Professional Ethics"
                ]
            }
        ],
        "related_interests": ["Technology", "Business"]
    },
    {
        "id": "foundation_phase_teacher",
        "title": "Foundation Phase Teacher",
        "description": "Teaches learners in Grades R–3, fostering literacy, numeracy and life skills.",
        "skills": [
            "Lesson planning",
            "Child development",
            "Classroom management",
            "Assessment techniques",
            "Communication"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Child Development Theories",
                    "Foundations of Education",
                    "Language Education I",
                    "Mathematics Education I"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Language Education II",
                    "Mathematics Education II",
                    "Creative Arts in Teaching",
                    "Classroom Management"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Assessment & Evaluation",
                    "Inclusive Education",
                    "Life Skills Education",
                    "Educational Technology"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Practicum I",
                    "Practicum II",
                    "Curriculum Design",
                    "Reflective Practice"
                ]
            }
        ],
        "related_interests": ["Education"]
    },
    {
        "id": "business_analyst",
        "title": "Business Analyst",
        "description": "Evaluates business processes and recommends improvements to drive efficiency.",
        "skills": [
            "Process mapping",
            "Data interpretation",
            "Stakeholder engagement",
            "Report writing",
            "Problem solving"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Principles of Commerce",
                    "Business Communication",
                    "Introduction to Economics",
                    "Quantitative Techniques I"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Management Accounting",
                    "Organizational Behaviour",
                    "Quantitative Techniques II",
                    "Information Systems"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Strategic Management",
                    "Project Management",
                    "Data Analytics for Business",
                    "Consulting Skills"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Business Project",
                    "Internship",
                    "Professional Ethics",
                    "Presentation Skills"
                ]
            }
        ],
        "related_interests": ["Business"]
    },
    {
        "id": "development_practitioner",
        "title": "Development Practitioner",
        "description": "Designs and implements programmes aimed at social and economic upliftment.",
        "skills": [
            "Project design",
            "Monitoring & evaluation",
            "Community engagement",
            "Policy analysis",
            "Grant writing"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Foundations of Development",
                    "Intro to Sociology",
                    "Research Methods I",
                    "Communication Skills"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Development Economics",
                    "Project Management I",
                    "Quantitative Methods",
                    "Stakeholder Analysis"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Policy & Governance",
                    "Monitoring & Evaluation",
                    "Research Methods II",
                    "Social Innovation"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Field Internship",
                    "Capstone Development Project",
                    "Leadership in Development",
                    "Ethics & Accountability"
                ]
            }
        ],
        "related_interests": ["Business", "Education"]
    },
    {
        "id": "public_administrator",
        "title": "Public Administrator",
        "description": "Manages operations, budgets and policies within government and public sector entities.",
        "skills": [
            "Policy development",
            "Budgeting",
            "Stakeholder management",
            "Regulatory compliance",
            "Strategic planning"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Administration",
                    "Public Policy Basics",
                    "Economics for Administrators",
                    "Business Communication"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Public Financial Management",
                    "Organizational Behaviour",
                    "Quantitative Analysis",
                    "Law & Ethics"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Strategic Management",
                    "Governance & Accountability",
                    "Project Management II",
                    "Risk Management"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Administrative Project",
                    "Internship",
                    "Ethical Leadership",
                    "Policy Analysis Workshop"
                ]
            }
        ],
        "related_interests": ["Business", "Law"]
    },
    {
        "id": "lawyer",
        "title": "Legal Practitioner",
        "description": "Advises clients, interprets legislation and represents in court or tribunals.",
        "skills": [
            "Legal research",
            "Argumentation",
            "Negotiation",
            "Drafting contracts",
            "Ethical judgement"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Legal Systems & Sources",
                    "Contract Law I",
                    "Intro to Legal Writing",
                    "Constitutional Law I"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Criminal Law I",
                    "Property Law I",
                    "Legal Research Methods",
                    "Ethics & Professional Conduct"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Civil Procedure",
                    "Commercial Law",
                    "Alternative Dispute Resolution",
                    "Clinical Legal Education I"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Bar Preparation",
                    "Internship / Clerkship",
                    "Advanced Advocacy",
                    "Professional Responsibility"
                ]
            }
        ],
        "related_interests": ["Law"]
    },
    {
        "id": "hotel_manager",
        "title": "Hotel Manager",
        "description": "Oversees all facets of hotel operations, from guest services to finance.",
        "skills": [
            "Hospitality operations",
            "Staff leadership",
            "Financial acumen",
            "Customer relations",
            "Quality assurance"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Hospitality",
                    "Food & Beverage Basics",
                    "Front Office Operations",
                    "Service Excellence"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Housekeeping Management",
                    "Cost Control",
                    "Revenue Management",
                    "Human Resources"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Strategic Marketing",
                    "Event Management",
                    "Quality & Safety",
                    "Technology in Hospitality"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Hospitality Project",
                    "Industry Placement",
                    "Leadership in Service",
                    "Business Planning"
                ]
            }
        ],
        "related_interests": ["Business", "Marketing"]
    },
    {
        "id": "event_manager",
        "title": "Event Manager",
        "description": "Plans, coordinates and executes events from concept through wrap‑up.",
        "skills": [
            "Project planning",
            "Vendor management",
            "Budgeting",
            "Marketing & promotion",
            "On‑site coordination"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Events",
                    "Principles of Marketing",
                    "Business Communication",
                    "Project Management I"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Budget & Contracts",
                    "Logistics & Operations",
                    "Sponsorship Management",
                    "Digital Promotion"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Risk Management",
                    "Experience Design",
                    "Stakeholder Engagement",
                    "Data Analytics for Events"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Event Project",
                    "Internship",
                    "Leadership & Negotiation",
                    "Ethical Practice"
                ]
            }
        ],
        "related_interests": ["Business", "Marketing", "Art & Design"]
    },
    {
        "id": "chef",
        "title": "Culinary Chef",
        "description": "Prepares and presents high‑quality dishes, oversees kitchen operations.",
        "skills": [
            "Recipe development",
            "Food safety",
            "Time management",
            "Cost control",
            "Team leadership"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Kitchen Fundamentals",
                    "Nutrition Basics",
                    "Food Safety & Hygiene",
                    "Basic Cooking Techniques"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "International Cuisines",
                    "Baking & Pastry",
                    "Menu Planning",
                    "Inventory Management"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Advanced Culinary Techniques",
                    "Nutrition & Special Diets",
                    "Kitchen Leadership",
                    "Food Styling"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Kitchen Project",
                    "Catering Management",
                    "Internship / Apprenticeship",
                    "Professional Portfolio"
                ]
            }
        ],
        "related_interests": ["Art & Design", "Business"]
    },
    {
        "id": "tourism_manager",
        "title": "Tourism Manager",
        "description": "Develops and markets tourism products and manages visitor experiences.",
        "skills": [
            "Destination marketing",
            "Customer service",
            "Itinerary planning",
            "Sustainability practices",
            "Stakeholder engagement"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Tourism",
                    "Principles of Marketing",
                    "Geography of Tourism",
                    "Business Communication"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Tourism Economics",
                    "Tour Operations Management",
                    "Digital Marketing",
                    "Sustainable Tourism"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Event & Conference Management",
                    "Customer Experience Design",
                    "Policy & Regulation",
                    "Research Methods"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Tourism Project",
                    "Industry Internship",
                    "Stakeholder Negotiation",
                    "Ethics & Accountability"
                ]
            }
        ],
        "related_interests": ["Business", "Marketing", "Art & Design"]
    },
    {
        "id": "research_analyst",
        "title": "Research Analyst",
        "description": "Designs and conducts research studies in social and cultural contexts.",
        "skills": [
            "Qualitative methods",
            "Quantitative analysis",
            "Report writing",
            "Critical thinking",
            "Stakeholder engagement"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Social Sciences",
                    "Research Methods I",
                    "Statistics I",
                    "Academic Writing"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Research Methods II",
                    "Statistics II",
                    "Ethics in Research",
                    "Data Visualization"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Thematic Analysis",
                    "Survey Design",
                    "Case Study Methods",
                    "Stakeholder Interviews"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Research Project",
                    "Industry Placement",
                    "Dissemination & Presentation",
                    "Grant Writing"
                ]
            }
        ],
        "related_interests": ["Science", "Business"]
    },
    {
        "id": "media_specialist",
        "title": "Media & Communications Specialist",
        "description": "Creates and manages content across print, digital and broadcast platforms.",
        "skills": [
            "Content creation",
            "Social media management",
            "Graphic design basics",
            "Audience analysis",
            "Writing & editing"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Intro to Media Studies",
                    "Writing for Media",
                    "Digital Literacy",
                    "Fundamentals of Design"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Social Media Strategies",
                    "Multimedia Production",
                    "Communication Theory",
                    "Analytics & Metrics"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Brand Management",
                    "Advanced Editing",
                    "Campaign Planning",
                    "Ethics & Law"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Capstone Media Project",
                    "Internship",
                    "Portfolio Development",
                    "Professional Networking"
                ]
            }
        ],
        "related_interests": ["Marketing", "Art & Design"]
    },
    {
        "id": "social_worker",
        "title": "Social Worker",
        "description": "Supports individuals and communities through counselling, advocacy and resource linkage.",
        "skills": [
            "Counselling",
            "Advocacy",
            "Case management",
            "Community outreach",
            "Ethical practice"
        ],
        "roadmap": [
            {
                "title": "Foundation",
                "year": "Year 1",
                "courses": [
                    "Introduction to Social Work",
                    "Human Behavior",
                    "Communication Skills",
                    "Ethics & Professionalism"
                ]
            },
            {
                "title": "Core Skills",
                "year": "Year 2",
                "courses": [
                    "Case Management",
                    "Psychosocial Assessment",
                    "Group Work Methods",
                    "Policy & Legislation"
                ]
            },
            {
                "title": "Advanced Techniques",
                "year": "Year 3",
                "courses": [
                    "Clinical Social Work",
                    "Community Development",
                    "Research Methods",
                    "Trauma-Informed Practice"
                ]
            },
            {
                "title": "Professional Practice",
                "year": "Year 4",
                "courses": [
                    "Field Practicum I",
                    "Field Practicum II",
                    "Professional Supervision",
                    "Capstone Reflection"
                ]
            }
        ],
        "related_interests": ["Healthcare", "Education"]
    }
]
# Modified upload logic
def upload_data():
    try:
        # Upload careers with enhanced fields
        for career in careers:
            doc_ref = db.collection("careers").document(career["id"])
            
            # Check if document exists
            if doc_ref.get().exists:
                logger.warning(f"Career {career['title']} already exists, skipping")
                continue
                
            # Add additional fields needed by assessment
            career_data = {
                **career,
                "personality_traits": ["analytical", "detail-oriented", "creative"],
                "values": ["achievement", "independence", "learning"],
                "postgraduate_pathways": career.get("postgraduate", [])
            }
            
            doc_ref.set(career_data)
            logger.info(f"Added career: {career['title']}")
        
        # Upload UMP courses with validation
        for faculty_name, schools in UMP_COURSES.items():
            doc_ref = db.collection("ump_courses").document(faculty_name)
            
            if doc_ref.get().exists:
                logger.warning(f"Faculty {faculty_name} already exists, skipping")
                continue
                
            school_list = []
            for school_name, programs in schools.items():
                school_entry = {
                    "name": school_name,
                    "undergraduate": programs.get("undergraduate", []),
                    "postgraduate": programs.get("postgraduate", [])
                }
                school_list.append(school_entry)

            doc_ref.set({
                "faculty": faculty_name,
                "schools": school_list
            })
            logger.info(f"✅ Uploaded faculty: {faculty_name} with {len(school_list)} schools")
            
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise

if __name__ == "__main__":
    upload_data()