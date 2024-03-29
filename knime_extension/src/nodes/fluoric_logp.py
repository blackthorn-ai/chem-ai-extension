import logging
import math

import pandas as pd
import knime.extension as knext

from utils.fluoriclogpka_utils import predict_logP

LOGGER = logging.getLogger(__name__)

@knext.node(name="Fluoric logP", node_type=knext.NodeType.LEARNER, icon_path="icons/chem_icon.png", category="/")
@knext.input_table(name="Input SMILES Data", description="Table with SMILES in 'string' of 'SMI' format")
@knext.output_table(name="Output Data", description="Table with predicted logP values")
class Fluoriclogp:
    """Node for predicting logP using molecules SMILES.
    For predicting are used a lot of generated molecule features, such as dihedral angle, molecular weight and volume, amount of Carbon atoms etc.
    All this molecule features used for predicting logP values using H2O models.
    """

    def configure(self, configure_context, input_schema_1):
        
        input_schema_1 = input_schema_1.append(knext.Column(knext.double(), "logP"))

        return input_schema_1

 
    def execute(self, exec_context, input_1):
        input_pandas = input_1.to_pandas()

        if "SMILES" not in input_pandas.columns:
            LOGGER.error(f"SMILES column is not represented in the input table.")
            raise ValueError("The table does not contain the column 'SMILES'.")

        predicted_logPs = []
        for _, row in input_pandas.iterrows():
            if pd.isnull(row['SMILES']):
                LOGGER.error(f"SMILES value cannot be NaN.")
                raise ValueError("SMILES cannot be NaN.")

            SMILES = row['SMILES']

            try:
                predicted_logP = predict_logP(SMILES=SMILES)
            except Exception as e:
                LOGGER.error(f"Error predicting logP for SMILES '{SMILES}': {str(e)}")
                raise ValueError(f"Inappropriate SMILES format: {SMILES}")
            
            predicted_logPs.append(predicted_logP)

        output_df = pd.DataFrame({
            'SMILES': input_pandas['SMILES'],
            'logP': predicted_logPs,
        })
        
        return knext.Table.from_pandas(output_df)
