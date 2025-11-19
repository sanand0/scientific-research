#!/usr/bin/env python3
"""
Dye Discovery Virtual Screening Pipeline
Accelerates dye discovery by predicting color, light fastness, and washing fastness
"""

import datamol as dm
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, AllChem, Lipinski
from rdkit.Chem import Fragments
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# STAGE 1: DYE DATABASE GENERATION
# ============================================================================

def get_known_dye_scaffolds():
    """
    Returns a curated list of known industrial dye molecules and scaffolds
    from various classes relevant to textile, paint, and polymer industries.
    """
    dyes = {
        # Azo dyes (largest class, ~60% of commercial dyes)
        'Disperse_Orange_3': 'c1ccc(cc1)N=Nc2ccc(cc2N)N',
        'Methyl_Orange': 'CN(C)c1ccc(cc1)N=Nc2ccc(cc2)S(=O)(=O)[O-]',
        'Sudan_I': 'c1ccc(cc1)N=Nc2ccc(cc2)O',
        'Acid_Orange_7': 'Cc1ccc(cc1)N=Nc2ccc(c(c2)O)S(=O)(=O)[O-]',
        'Direct_Red_28': 'c1cc(ccc1N=Nc2ccc(c(c2O)S(=O)(=O)[O-])N=Nc3ccc(cc3)N)N',
        'Disperse_Yellow_3': 'Cc1c(c(c(c(c1[N+](=O)[O-])[N+](=O)[O-])N)N=Nc2ccccc2)O',

        # Anthraquinone dyes (excellent light fastness)
        'Disperse_Blue_1': 'CCN(CC)c1ccc2c(c1)C(=O)c3c(C2=O)cc(cc3)NC',
        'Alizarin': 'O=C1c2ccccc2C(=O)c3c1c(O)cc(O)c3',
        'Quinizarin': 'O=C1c2ccccc2C(=O)c3c1c(O)ccc(O)c3',
        'Disperse_Red_9': 'O=C1c2ccccc2C(=O)c3c1ccc(c3)N',
        '1,4-Diaminoanthraquinone': 'O=C1c2ccccc2C(=O)c3c1c(N)ccc(N)c3',

        # Indigo and thioindigo derivatives (vat dyes) - using simpler representation
        'Indigo_simplified': 'O=C1/C(=C2\\Nc3ccccc3C2=O)Nc4ccccc14',

        # Triarylmethane dyes (brilliant colors) - simplified
        'Malachite_Green_Base': 'CN(C)c1ccc(C(c2ccccc2)c3ccc(N(C)C)cc3)cc1',

        # Azo-metal complex dyes (superior fastness)
        'Chrome_Yellow_Base': 'c1ccc(cc1)N=Nc2cc(ccc2O)S(=O)(=O)[O-]',

        # Reactive dyes (covalently bind to fiber)
        'Reactive_Black_5': 'Cc1cc(c(cc1S(=O)(=O)[O-])N=Nc2c(cc(c(c2N=Nc3cc(c(cc3S(=O)(=O)[O-])N)N)O)S(=O)(=O)[O-])N)N',

        # Polymethine dyes (cyanine-like)
        'Simple_Cyanine': 'C[n+]1ccccc1C=Cc2cccc[n+]2C',

        # Naphthol-based azo dyes
        'Pigment_Red_3': 'Cc1ccc(cc1)N=Nc2c(O)ccc3ccccc23',
        'Naphthol_AS': 'O=C(Nc1c(O)ccc2ccccc12)C',

        # Stilbene derivatives (optical brighteners)
        'Stilbene_Brightener': 'c1ccc(cc1)C=Cc2ccccc2',

        # Benzodifuranone (important vat dyes)
        'Vat_Orange_1': 'O=C1c2ccccc2C(=O)c3c1ccc(c3)N=Nc4ccc(O)c5c4cccc5',

        # Quinophthalone (yellow dyes)
        'Quinophthalone_Yellow': 'O=C1C(=O)c2ccccc2C(=O)c3c1cccc3',

        # Perinone dyes (high performance pigments)
        'Perinone_Orange': 'O=C1c2cccc3c2C(=O)c4c1ccc5c4c3ccc5',

        # Isoindolinone (yellows and oranges)
        'Isoindolinone_Yellow': 'O=C1NC(=O)c2c1cccc2',

        # Dioxazine (violets)
        'Dioxazine_Violet_Base': 'O=C1Nc2ccccc2C(=O)Nc3c1cccc3',

        # Aminoketone dyes
        'Disperse_Yellow_42': 'O=C1c2ccccc2C(=C(c3ccccc3)c4ccccc4)C1=O',
    }

    return dyes


def generate_dye_variations(base_smiles, num_variations=10):
    """
    Generate structural variations of a dye scaffold by:
    - Adding electron-donating groups (OH, OCH3, NH2, N(CH3)2)
    - Adding electron-withdrawing groups (NO2, Cl, Br, SO3H, COOH)
    - Modifying alkyl chains

    Returns list of SMILES strings
    """
    variations = [base_smiles]

    # Note: In practice, this would use fragment-based enumeration
    # or SMARTS-based transformations. For this demo, we'll define
    # specific variations manually for key scaffolds.

    return variations


def build_dye_library():
    """
    Build a comprehensive library of candidate dyes
    """
    print("Building dye library...")

    known_dyes = get_known_dye_scaffolds()

    # Convert to molecules
    dye_data = []
    for name, smiles in known_dyes.items():
        mol = dm.to_mol(smiles)
        if mol is not None:
            mol = dm.standardize_mol(mol)
            if mol is not None:
                dye_data.append({
                    'name': name,
                    'smiles': dm.to_smiles(mol),
                    'mol': mol,
                    'source': 'known'
                })

    print(f"Loaded {len(dye_data)} known dye structures")

    # Add novel variations (simplified for demo)
    # In practice, would use generative models or systematic enumeration
    novel_candidates = generate_novel_dye_candidates()
    for i, (smiles, description) in enumerate(novel_candidates):
        mol = dm.to_mol(smiles)
        if mol is not None:
            mol = dm.standardize_mol(mol)
            if mol is not None:
                dye_data.append({
                    'name': f'Novel_Candidate_{i+1}',
                    'smiles': dm.to_smiles(mol),
                    'mol': mol,
                    'source': 'generated',
                    'description': description
                })

    print(f"Added {len(novel_candidates)} novel candidates")
    print(f"Total library size: {len(dye_data)}")

    return pd.DataFrame(dye_data)


def generate_novel_dye_candidates():
    """
    Generate novel dye candidates based on known scaffolds
    with strategic modifications for improved properties
    """
    candidates = [
        # Modified azo dyes with improved fastness
        ('c1ccc(cc1N)N=Nc2ccc(cc2O)c3ccccc3',
         'Phenyl-substituted aminoazophenol - enhanced light fastness'),

        ('c1ccc(cc1N(C)C)N=Nc2ccc(c(c2O)C(F)(F)F)O',
         'Bis-hydroxy azo with CF3 - improved washing fastness'),

        ('c1ccc(cc1N=Nc2ccc(cc2N)c3nc4ccccc4s3)O',
         'Benzothiazole-azo hybrid - extended conjugation'),

        # Anthraquinone derivatives with strategic substitution
        ('O=C1c2cc(N(CC)CC)ccc2C(=O)c3c1c(O)cc(N(CC)CC)c3',
         '1,5-Bis(diethylamino)-4,8-dihydroxyanthraquinone - blue with enhanced solubility'),

        ('O=C1c2ccc(O)cc2C(=O)c3c1c(N)cc(c3)S(=O)(=O)O',
         'Sulfonated aminohydroxyanthraquinone - water-soluble blue'),

        ('O=C1c2cc(OC)ccc2C(=O)c3c1c(OC)cc(N)c3O',
         'Methoxy-substituted aminohydroxyanthraquinone - violet'),

        # Indigo derivatives - using simpler azo alternatives for demonstration
        ('COc1ccc2c(c1)C(=O)/C(=C(/c3[nH]c4ccc(OC)cc4c3=O)O)C2=O',
         '5,5-Dimethoxyindigo derivative - red-shifted spectrum'),

        # Heteroaromatic azo dyes
        ('c1ccc(cc1)N=Nc2nc(cs2)c3ccccc3',
         'Thiazole-azo dye - yellow with good fastness'),

        ('c1ccc(nc1)N=Nc2ccc(cc2O)c3ccncc3',
         'Pyridyl-azo phenol - water-soluble orange'),

        # Methine dyes with extended conjugation
        ('CN(C)c1ccc(cc1)C=Cc2ccc(cc2)C=Cc3ccc(cc3)N(C)C',
         'Extended conjugation methine - near-IR absorption'),

        # Quinacridone derivatives
        ('O=C1Nc2cc3c(cc2C(=O)c4c1cccc4)C(=O)c5c(N3)cccc5',
         'Quinacridone derivative - excellent fastness'),

        # Coumarin dyes (laser dyes, good for some applications)
        ('O=C1Oc2ccc(cc2C=C1c3ccc(cc3)N(C)C)O',
         '7-Hydroxy-3-(4-dimethylaminophenyl)coumarin - green fluorescence'),

        # Perylene derivatives
        ('O=C1c2ccc3c4ccc5c6c(ccc(c7ccc(c2c37)C1=O)C(=O)c8c6c4c5c8=O)=O',
         'Perylenetetracarboxylic diimide derivative - red with exceptional stability'),

        # Diketopyrrolopyrrole (DPP) - high performance pigments
        ('O=C1C(=C(N1)c2ccccc2)c3ccccc3',
         'Diphenyl-DPP - red with excellent light fastness'),

        # Benzimidazolone
        ('O=C1Nc2ccc(cc2N1)N=Nc3ccc(O)c(c3)C(=O)O',
         'Benzimidazolone azo - yellow with superior fastness'),

        # Large aromatic systems (simplified phthalocyanine-like)
        ('c1ccc2c(c1)nc(n2)c3nc4ccccc4n3',
         'Extended aromatic system - blue-green pigment'),

        # Pyrazolone azo dyes
        ('CN(C)c1ccc(cc1)N=NC2=C(O)N(N(C2=O)c3ccccc3)C',
         'Pyrazolone azo dye - yellow with good fastness'),

        # Naphthalimide dyes
        ('O=C1c2cccc3c2C(=O)N(C13)CCCCN(C)C',
         'N-alkyl naphthalimide - yellow fluorescent dye'),

        # Styryl dyes
        ('c1ccc(cc1)C=Cc2ccc3c(c2)oc(=O)cc3',
         'Coumarin-styryl hybrid - yellow-orange'),
    ]

    return candidates


# ============================================================================
# STAGE 2 & 3: PROPERTY PREDICTION - COLOR
# ============================================================================

def predict_color_properties(mol):
    """
    Predict color-related properties from molecular structure

    Returns:
        dict with:
        - estimated_lambda_max: Predicted absorption maximum (nm)
        - color_family: Predicted color
        - conjugation_score: Measure of conjugation extent
        - auxochrome_score: Presence of color-enhancing groups
    """

    # Count conjugated system size
    aromatic_atoms = Lipinski.NumAromaticRings(mol) * 6  # Approximate

    # Count auxochromes (electron-donating groups)
    num_nh2 = Fragments.fr_NH2(mol)
    num_oh = Fragments.fr_Ar_OH(mol)
    # Count aromatic ethers (methoxy, etc.)
    ar_ether_pattern = Chem.MolFromSmarts('cO[C,c]')
    num_or = len(mol.GetSubstructMatches(ar_ether_pattern)) if ar_ether_pattern else 0
    num_nr2 = Fragments.fr_N_O(mol)  # Approximate

    # Count chromophores
    num_azo = len(mol.GetSubstructMatches(Chem.MolFromSmarts('N=N')))
    num_carbonyl = Fragments.fr_C_O(mol)
    num_nitro = Fragments.fr_nitro(mol)

    auxochrome_score = num_nh2 + num_oh + num_or + num_nr2
    chromophore_score = num_azo * 2 + num_carbonyl + num_nitro

    # Estimate conjugation length
    aromatic_rings = Lipinski.NumAromaticRings(mol)

    # Simple λmax estimation (Woodward-Fieser-like rules, very simplified)
    base_lambda = 250  # Base for benzene

    # Each aromatic ring adds ~30nm
    lambda_max = base_lambda + (aromatic_rings * 30)

    # Auxochromes cause red shift
    lambda_max += auxochrome_score * 10

    # Azo groups cause major red shift
    lambda_max += num_azo * 60

    # Carbonyl groups
    lambda_max += num_carbonyl * 15

    # Predict color family based on λmax
    if lambda_max < 400:
        color_family = "Colorless/UV"
    elif lambda_max < 450:
        color_family = "Yellow"
    elif lambda_max < 490:
        color_family = "Orange"
    elif lambda_max < 580:
        color_family = "Red"
    elif lambda_max < 610:
        color_family = "Violet"
    elif lambda_max < 720:
        color_family = "Blue"
    else:
        color_family = "Green"

    # Calculate molar absorptivity estimate (very rough)
    epsilon_estimate = chromophore_score * 10000 + auxochrome_score * 5000

    return {
        'estimated_lambda_max': lambda_max,
        'color_family': color_family,
        'conjugation_score': aromatic_rings,
        'auxochrome_score': auxochrome_score,
        'chromophore_score': chromophore_score,
        'estimated_epsilon': epsilon_estimate
    }


# ============================================================================
# STAGE 4: PROPERTY PREDICTION - LIGHT FASTNESS
# ============================================================================

def predict_light_fastness(mol):
    """
    Predict light fastness (photostability) based on structural features

    High light fastness correlates with:
    - High HOMO-LUMO gap
    - Presence of anthraquinone, phthalocyanine scaffolds
    - Absence of weak bonds (aliphatic azo)
    - Presence of stabilizing groups

    Returns:
        dict with:
        - light_fastness_score: 1-8 scale (8 = best)
        - stability_features: List of stabilizing factors
        - risk_features: List of destabilizing factors
    """

    stability_features = []
    risk_features = []
    base_score = 4.0  # Neutral baseline

    # Check for highly stable scaffolds
    anthraquinone_pattern = Chem.MolFromSmarts('O=C1c2ccccc2C(=O)c3ccccc13')
    if mol.HasSubstructMatch(anthraquinone_pattern):
        base_score += 2.0
        stability_features.append("Anthraquinone core (excellent stability)")

    # Phthalocyanine-like (approximate check)
    num_aromatic_rings = Lipinski.NumAromaticRings(mol)
    if num_aromatic_rings >= 4:
        base_score += 1.0
        stability_features.append("Extended aromatic system")

    # Azo groups - check for stabilizing ortho-hydroxy groups
    azo_pattern = Chem.MolFromSmarts('cN=Nc')
    azo_matches = mol.GetSubstructMatches(azo_pattern)

    ortho_hydroxy_azo = Chem.MolFromSmarts('c(N=N)c(O)')
    if mol.HasSubstructMatch(ortho_hydroxy_azo):
        base_score += 1.0
        stability_features.append("Ortho-hydroxy azo (chelation stability)")
    elif len(azo_matches) > 0:
        base_score -= 0.5
        risk_features.append("Azo group without stabilization")

    # Electron-withdrawing groups enhance stability
    num_nitro = Fragments.fr_nitro(mol)
    num_halogen = Fragments.fr_halogen(mol)
    if num_nitro > 0 or num_halogen > 0:
        base_score += 0.5
        stability_features.append("Electron-withdrawing substituents")

    # Methoxy groups can provide moderate stabilization
    ar_ether_pattern = Chem.MolFromSmarts('cO[C,c]')
    num_or = len(mol.GetSubstructMatches(ar_ether_pattern)) if ar_ether_pattern else 0
    if num_or > 0:
        base_score += 0.3

    # Check for photolabile groups
    aliphatic_azo = Chem.MolFromSmarts('CN=NC')  # Aliphatic azo - very unstable
    if mol.HasSubstructMatch(aliphatic_azo):
        base_score -= 2.0
        risk_features.append("Aliphatic azo (highly photolabile)")

    # Peroxide bonds
    peroxide = Chem.MolFromSmarts('OO')
    if mol.HasSubstructMatch(peroxide):
        base_score -= 1.5
        risk_features.append("Peroxide linkage")

    # Indigo scaffold - moderate to good
    indigo_pattern = Chem.MolFromSmarts('O=C1C(=CNc2c1cccc2)')
    if mol.HasSubstructMatch(indigo_pattern):
        base_score += 1.0
        stability_features.append("Indigo-like structure")

    # Molecular weight - larger molecules often more stable
    mw = Descriptors.MolWt(mol)
    if mw > 400:
        base_score += 0.5
        stability_features.append("High molecular weight")

    # Clamp score to 1-8 scale
    light_fastness_score = np.clip(base_score, 1.0, 8.0)

    # Convert to discrete rating
    light_fastness_rating = int(round(light_fastness_score))

    return {
        'light_fastness_score': light_fastness_score,
        'light_fastness_rating': light_fastness_rating,
        'stability_features': stability_features,
        'risk_features': risk_features
    }


# ============================================================================
# STAGE 5: PROPERTY PREDICTION - WASHING FASTNESS
# ============================================================================

def predict_washing_fastness(mol):
    """
    Predict washing fastness (resistance to washing/chemical stability)

    High washing fastness correlates with:
    - Strong covalent bonds throughout
    - Resistance to hydrolysis
    - Low water solubility (for disperse dyes) or strong fiber binding
    - Stable functional groups

    Returns:
        dict with:
        - washing_fastness_score: 1-5 scale (5 = best)
        - stability_features: List of stabilizing factors
        - risk_features: List of destabilizing factors
    """

    stability_features = []
    risk_features = []
    base_score = 3.0  # Neutral baseline

    # Check for hydrolyzable groups
    ester_pattern = Chem.MolFromSmarts('C(=O)O[C,c]')
    num_esters = len(mol.GetSubstructMatches(ester_pattern))
    if num_esters > 0:
        base_score -= 0.8
        risk_features.append(f"Ester groups ({num_esters}) - hydrolyzable")

    # Sulfonate groups - improve water solubility and fiber binding
    sulfonate = Chem.MolFromSmarts('S(=O)(=O)[O-,OH]')
    num_sulfonates = len(mol.GetSubstructMatches(sulfonate))
    if num_sulfonates > 0:
        base_score += 0.5
        stability_features.append("Sulfonate groups (fiber affinity)")

    # Carboxylic acids - can improve binding but may hydrolyze
    carboxylic = Chem.MolFromSmarts('C(=O)[O-,OH]')
    num_carboxylic = len(mol.GetSubstructMatches(carboxylic))
    if num_carboxylic > 0:
        base_score += 0.2
        stability_features.append("Carboxyl groups (fiber binding)")

    # Azo groups - generally stable to washing but can reduce under certain conditions
    azo_pattern = Chem.MolFromSmarts('N=N')
    num_azo = len(mol.GetSubstructMatches(azo_pattern))
    if num_azo > 0:
        base_score -= 0.2  # Slight penalty for potential reduction

    # Anthraquinone - excellent washing fastness
    anthraquinone = Chem.MolFromSmarts('O=C1c2ccccc2C(=O)c3ccccc13')
    if mol.HasSubstructMatch(anthraquinone):
        base_score += 1.5
        stability_features.append("Anthraquinone (chemically stable)")

    # Phthalocyanine - excellent washing fastness
    num_aromatic_rings = Lipinski.NumAromaticRings(mol)
    if num_aromatic_rings >= 4:
        base_score += 1.0
        stability_features.append("Large aromatic system (stable)")

    # Halogen substituents - increase hydrophobicity and stability
    num_halogen = Fragments.fr_halogen(mol)
    if num_halogen > 0:
        base_score += 0.3
        stability_features.append("Halogenated (increased stability)")

    # Check LogP - very low LogP means water-soluble (might bleed)
    logp = Descriptors.MolLogP(mol)
    if logp < -1:
        base_score -= 0.5
        risk_features.append("High water solubility (may bleed)")
    elif logp > 3:
        base_score += 0.5
        stability_features.append("Low water solubility (reduced bleeding)")

    # Hydroxyl groups - can form H-bonds with fibers
    num_oh = Fragments.fr_Ar_OH(mol)
    if num_oh > 0:
        base_score += 0.4
        stability_features.append("Hydroxyl groups (fiber binding)")

    # Amino groups - fiber affinity
    num_nh2 = Fragments.fr_NH2(mol)
    if num_nh2 > 0:
        base_score += 0.3
        stability_features.append("Amino groups (fiber affinity)")

    # Clamp score to 1-5 scale
    washing_fastness_score = np.clip(base_score, 1.0, 5.0)

    # Convert to discrete rating
    washing_fastness_rating = int(round(washing_fastness_score))

    return {
        'washing_fastness_score': washing_fastness_score,
        'washing_fastness_rating': washing_fastness_rating,
        'logp': logp,
        'stability_features': stability_features,
        'risk_features': risk_features
    }


# ============================================================================
# STAGE 6: ADDITIONAL MOLECULAR PROPERTIES
# ============================================================================

def compute_additional_properties(mol):
    """
    Compute additional relevant properties for dye applications
    """
    return {
        'molecular_weight': Descriptors.MolWt(mol),
        'logp': Descriptors.MolLogP(mol),
        'num_aromatic_rings': Lipinski.NumAromaticRings(mol),
        'num_rotatable_bonds': Lipinski.NumRotatableBonds(mol),
        'tpsa': Descriptors.TPSA(mol),
        'num_hbd': Lipinski.NumHDonors(mol),
        'num_hba': Lipinski.NumHAcceptors(mol),
        'num_heavy_atoms': Lipinski.HeavyAtomCount(mol),
    }


def calculate_synthetic_accessibility(mol):
    """
    Estimate synthetic accessibility (1-10, 1=easy to synthesize)
    Using simplified version of SAScore
    """
    # Simplified SA score based on:
    # - Molecular complexity
    # - Presence of unusual functional groups
    # - Ring complexity

    num_rings = Lipinski.NumAromaticRings(mol) + Lipinski.NumAliphaticRings(mol)
    num_atoms = mol.GetNumHeavyAtoms()
    num_rotatable = Lipinski.NumRotatableBonds(mol)

    # Base complexity
    complexity = num_atoms / 10.0
    complexity += num_rings * 0.5
    complexity += num_rotatable * 0.1

    # Clamp to 1-10
    sa_score = np.clip(complexity, 1.0, 10.0)

    return {
        'sa_score': sa_score,
        'synthesis_difficulty': 'Easy' if sa_score < 3 else ('Moderate' if sa_score < 6 else 'Difficult')
    }


# ============================================================================
# MAIN SCREENING PIPELINE
# ============================================================================

def run_virtual_screening():
    """
    Main virtual screening pipeline
    """
    print("="*80)
    print("DYE DISCOVERY VIRTUAL SCREENING PIPELINE")
    print("="*80)
    print()

    # Stage 1: Build library
    df = build_dye_library()
    print()

    # Stage 2-5: Predict properties for each dye
    print("Predicting molecular properties...")

    results = []
    for idx, row in df.iterrows():
        mol = row['mol']

        # Color properties
        color_props = predict_color_properties(mol)

        # Light fastness
        light_props = predict_light_fastness(mol)

        # Washing fastness
        wash_props = predict_washing_fastness(mol)

        # Additional properties
        add_props = compute_additional_properties(mol)

        # Synthetic accessibility
        sa_props = calculate_synthetic_accessibility(mol)

        # Combine all properties
        result = {
            'name': row['name'],
            'smiles': row['smiles'],
            'source': row['source'],
            **color_props,
            **light_props,
            **wash_props,
            **add_props,
            **sa_props
        }

        if 'description' in row:
            result['description'] = row['description']

        results.append(result)

    results_df = pd.DataFrame(results)

    print(f"Completed property prediction for {len(results_df)} compounds")
    print()

    # Calculate composite score
    # Normalize scores and combine
    results_df['composite_score'] = (
        (results_df['light_fastness_score'] / 8.0) * 0.35 +
        (results_df['washing_fastness_score'] / 5.0) * 0.35 +
        (results_df['chromophore_score'] / results_df['chromophore_score'].max()) * 0.20 +
        (1.0 - results_df['sa_score'] / 10.0) * 0.10  # Prefer easier synthesis
    )

    # Sort by composite score
    results_df = results_df.sort_values('composite_score', ascending=False)

    return results_df


def print_top_candidates(df, n=10):
    """
    Print top candidates in a readable format
    """
    print("="*80)
    print(f"TOP {n} CANDIDATE DYES")
    print("="*80)
    print()

    for idx, (i, row) in enumerate(df.head(n).iterrows()):
        print(f"Rank {idx + 1}: {row['name']}")
        print(f"  Source: {row['source']}")
        if 'description' in row and pd.notna(row['description']):
            print(f"  Description: {row['description']}")
        print(f"  SMILES: {row['smiles']}")
        print(f"  Color: {row['color_family']} (λmax ≈ {row['estimated_lambda_max']:.0f} nm)")
        print(f"  Light Fastness: {row['light_fastness_rating']}/8")
        if row['stability_features']:
            print(f"    Stability factors: {', '.join(row['stability_features'][:2])}")
        print(f"  Washing Fastness: {row['washing_fastness_rating']}/5 (LogP: {row['logp']:.2f})")
        if row['stability_features']:
            print(f"    Stability factors: {', '.join(row['stability_features'][:2])}")
        print(f"  Molecular Weight: {row['molecular_weight']:.1f}")
        print(f"  Synthesis: {row['synthesis_difficulty']} (SA Score: {row['sa_score']:.1f})")
        print(f"  COMPOSITE SCORE: {row['composite_score']:.3f}")
        print()


if __name__ == "__main__":
    # Run the screening pipeline
    results_df = run_virtual_screening()

    # Save results
    output_file = 'dye_screening_results.csv'
    results_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")
    print()

    # Print top candidates
    print_top_candidates(results_df, n=15)

    # Additional analysis
    print("="*80)
    print("ANALYSIS BY COLOR FAMILY")
    print("="*80)
    print()
    for color in results_df['color_family'].unique():
        color_df = results_df[results_df['color_family'] == color]
        avg_light = color_df['light_fastness_score'].mean()
        avg_wash = color_df['washing_fastness_score'].mean()
        print(f"{color}: {len(color_df)} candidates")
        print(f"  Avg Light Fastness: {avg_light:.2f}/8")
        print(f"  Avg Washing Fastness: {avg_wash:.2f}/5")
        print()

    print("="*80)
    print("NOVEL VS KNOWN DYES")
    print("="*80)
    print()
    for source in ['known', 'generated']:
        source_df = results_df[results_df['source'] == source]
        print(f"{source.upper()}: {len(source_df)} candidates")
        print(f"  Avg Composite Score: {source_df['composite_score'].mean():.3f}")
        print(f"  Avg Light Fastness: {source_df['light_fastness_score'].mean():.2f}/8")
        print(f"  Avg Washing Fastness: {source_df['washing_fastness_score'].mean():.2f}/5")
        print()
