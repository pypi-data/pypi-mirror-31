# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

# NOTES:
#  * COULD NOT IMPLEMENT integrator_function in paramClassDefaults (see notes below)
#  * NOW THAT NOISE AND SMOOTHING_FACTOR ARE PROPRETIES THAT DIRECTLY REFERERNCE integrator_function,
#      SHOULD THEY NOW BE VALIDATED ONLY THERE (AND NOT IN TransferMechanism)??
#  * ARE THOSE THE ONLY TWO integrator PARAMS THAT SHOULD BE PROPERTIES??

# ****************************************  RecurrentTransferMechanism *************************************************

"""
.. _Recurrent_Transfer_Overview:

Overview
--------

A RecurrentTransferMechanism is a subclass of `TransferMechanism` that implements a single-layered recurrent
network, in which each element is connected to every other element (instantiated in a recurrent
`AutoAssociativeProjection` referenced by the Mechanism's `matrix <RecurrentTransferMechanism.matrix>` parameter).
It can report the energy and, if appropriate, the entropy of its output, and can be configured to implement
autoassociative (e.g., Hebbian) learning.

.. _Recurrent_Transfer_Creation:

Creating a RecurrentTransferMechanism
-------------------------------------

A RecurrentTransferMechanism is created directly by calling its constructor.::

    import psyneulink as pnl
    my_linear_recurrent_transfer_mechanism = pnl.RecurrentTransferMechanism(function=pnl.Linear)
    my_logistic_recurrent_transfer_mechanism = pnl.RecurrentTransferMechanism(function=pnl.Logistic(gain=1.0,
                                                                                                    bias=-4.0))

The recurrent projection is automatically created using (1) the **matrix** argument or (2) the **auto** and **hetero**
arguments of the Mechanism's constructor, and is assigned to the mechanism's `recurrent_projection
<RecurrentTransferMechanism.recurrent_projection>` attribute.

If the **matrix** argument is used to create the recurrent projection, it must specify either a square matrix or an
`AutoAssociativeProjection` that uses one (the default is `HOLLOW_MATRIX`).::

    recurrent_mech_1 = pnl.RecurrentTransferMechanism(default_variable=[[0.0, 0.0, 0.0]],
                                                      matrix=[[1.0, 2.0, 2.0],
                                                              [2.0, 1.0, 2.0],
                                                              [2.0, 2.0, 1.0]])

    recurrent_mech_2 = pnl.RecurrentTransferMechanism(default_variable=[[0.0, 0.0, 0.0]],
                                                      matrix=pnl.AutoAssociativeProjection)

If the **auto** and **hetero** arguments are used to create the recurrent projection, they set the diagonal and
off-diagonal terms, respectively.::

    recurrent_mech_3 = pnl.RecurrentTransferMechanism(default_variable=[[0.0, 0.0, 0.0]],
                                                      auto=1.0,
                                                      hetero=2.0)

.. note::

    In the examples above, recurrent_mech_1 and recurrent_mech_3 are identical.

In all other respects, a RecurrentTransferMechanism is specified in the same way as a standard `TransferMechanism`.

.. _Recurrent_Transfer_Learning:

Configuring Learning
~~~~~~~~~~~~~~~~~~~~

A RecurrentTransferMechanism can be configured for learning when it is created by assigning `True` to the
**enable_learning** argument of its constructor.  This creates an `AutoAssociativeLearningMechanism` that is used to
train its `recurrent_projection <RecurrentTransferMechanism.recurrent_projection>`, and assigns as its `function
<Function_Base.function>` the one  specified in the **learning_function** argument of the RecurrentTransferMechanism's
constructor.  By default, this is the `Hebbian` Function;  however, it can be replaced by any other function that is
suitable for autoassociative learning;  that is, one that takes a list or 1d array of numeric values
(an "activity vector") and returns a 2d array or square matrix (the "weight change matrix") with the same dimensions
as the length of the activity vector. The AutoAssociativeLearningMechanism is assigned to the `learning_mechanism
<RecurrentTransferMechanism.learning_mechanism>` attribute and is used to modify the `matrix
<AutoAssociativeProjection.matrix>` parameter of its `recurrent_projection
<RecurrentTransferMechanism.recurrent_projection>` (also referenced by the RecurrentTransferMechanism's own `matrix
<RecurrentTransferMechanism.matrix>` parameter.

If a RecurrentTransferMechanism is created without configuring learning (i.e., **enable_learning** is assigned `False`
in its constructor -- the default value), then learning cannot be enabled for the Mechanism until it has been
configured for learning;  any attempt to do so will issue a warning and then be ignored.  Learning can be configured
once the Mechanism has been created by calling its `configure_learning <RecurrentTransferMechanism.configure_learning>`
method, which also enables learning.

COMMENT:
8/7/17 CW: In past versions, the first sentence of the paragraph above was: "A RecurrentTransferMechanism can be
created directly by calling its constructor, or using the `mechanism() <Mechanism.mechanism>` command and specifying
RECURRENT_TRANSFER_MECHANISM as its **mech_spec** argument".
However, the latter method is no longer correct: it instead creates a DDM: the problem is line 590 in Mechanism.py,
as MechanismRegistry is empty!
10/9/17 MANTEL: mechanism() factory method is removed
COMMENT

.. _Recurrent_Transfer_Structure:

Structure
---------

The distinguishing feature of a RecurrentTransferMechanism is a self-projecting `AutoAssociativeProjection` -- that
is, one that projects from the Mechanism's `primary OutputState <OutputState_Primary>` back to its `primary
InputState <InputState_Primary>`.  This can be parameterized using its `matrix <RecurrentTransferMechanism.matrix>`,
`auto <RecurrentTransferMechanism.auto>`, and `hetero <RecurrentTransferMechanism.hetero>` attributes, and is
stored in its `recurrent_projection <RecurrentTransferMechanism.recurrent_projection>` attribute.

A RecurrentTransferMechanism also has two additional `OutputStates <OutputState>:  an *ENERGY* OutputState and, if its
`function <RecurrentTransferMechanism.function>` is bounded between 0 and 1 (e.g., a `Logistic` function), an *ENTROPY*
OutputState.  Each of these report the respective values of the vector in it its *RESULTS* (`primary
<OutputState_Primary>`) OutputState.

Finally, if it has been `specified for learning <Recurrent_Transfer_Learning>`, the RecurrentTransferMechanism is
associated with an `AutoAssociativeLearningMechanism` that is used to train its `AutoAssociativeProjection`.
The `learning_enabled <RecurrentTransferMechanism.learning_enabled>` attribute indicates whether learning
is enabled or disabled for the Mechanism.  If learning was not configured when the Mechanism was created, then it cannot
be enabled until the Mechanism is `configured for learning <Recurrent_Transfer_Learning>`.

In all other respects the Mechanism is identical to a standard  `TransferMechanism`.

.. _Recurrent_Transfer_Execution:

Execution
---------

When a RecurrentTransferMechanism executes, its variable, as is the case with all mechanisms, is determined by the
projections the mechanism receives. This means that a RecurrentTransferMechanism's variable is determined in part by the
value of its own `primary OutputState <OutputState_Primary>` on the previous execution, and the `matrix` of the
recurrent projection.

COMMENT:
Previous version of sentence above: "When a RecurrentTransferMechanism executes, it includes in its input the value of
its `primary OutputState <OutputState_Primary>` from its last execution."
8/9/17 CW: Changed the sentence above. Rationale: If we're referring to the fact that the recurrent projection
takes the previous output before adding it to the next input, we should specifically mention the matrix transformation
that occurs along the way.

12/1/17 KAM: Changed the above to describe the RecurrentTransferMechanism's variable on this execution in terms of
projections received, which happens to include a recurrent projection from its own primary output state on the previous
execution
COMMENT

Like a `TransferMechanism`, the function used to update each element can be assigned using its `function
<RecurrentTransferMechanism.function>` parameter. It then transforms its input
(including from the recurrent projection) using the specified function and parameters (see `Transfer_Execution`),
and returns the results in its OutputStates.

If it has been `configured for learning <Recurrent_Transfer_Learning>`
and is executed as part of a `System`, then its associated `LearningMechanism` is executed during the `learning phase
<System_Learning>` of the `System's execution <System_Execution>`.

.. _Recurrent_Transfer_Class_Reference:

Class Reference
---------------

"""

import numbers
from collections import Iterable

import numpy as np
import typecheck as tc

from psyneulink.components.functions.function import Hebbian, Linear, Stability, get_matrix, is_function_type
from psyneulink.components.mechanisms.adaptive.learning.learningmechanism import \
    ACTIVATION_INPUT, LEARNING_SIGNAL, LearningMechanism
from psyneulink.components.mechanisms.mechanism import Mechanism_Base
from psyneulink.components.mechanisms.processing.transfermechanism import TransferMechanism
from psyneulink.components.projections.modulatory.learningprojection import LearningProjection
from psyneulink.components.projections.pathway.mappingprojection import MappingProjection
from psyneulink.components.states.outputstate import PRIMARY, StandardOutputStates
from psyneulink.components.states.parameterstate import ParameterState
from psyneulink.components.states.state import _instantiate_state
from psyneulink.globals.keywords import \
    AUTO, ENERGY, ENTROPY, HETERO, HOLLOW_MATRIX, MATRIX, MEAN, MEDIAN, NAME, \
    PARAMS_CURRENT, RECURRENT_TRANSFER_MECHANISM, RESULT, STANDARD_DEVIATION, VARIANCE
from psyneulink.globals.context import ContextFlags
from psyneulink.globals.preferences.componentpreferenceset import is_pref_set
from psyneulink.globals.utilities import is_numeric_or_none, parameter_spec
from psyneulink.library.mechanisms.adaptive.learning.autoassociativelearningmechanism import \
    AutoAssociativeLearningMechanism

__all__ = [
    'DECAY', 'RECURRENT_OUTPUT', 'RecurrentTransferError', 'RecurrentTransferMechanism',
]

class RecurrentTransferError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value

    def __str__(self):
        return repr(self.error_value)

DECAY = 'decay'

# This is a convenience class that provides list of standard_output_state names in IDE
class RECURRENT_OUTPUT():

    """
        .. _RecurrentTransferMechanism_Standard_OutputStates:

        `Standard OutputStates <OutputState_Standard>` for
        `RecurrentTransferMechanism`

        .. TRANSFER_RESULT:

        *RESULT* : 1d np.array
            the result of the `function <RecurrentTransferMechanism.function>`
            of the Mechanism

        .. TRANSFER_MEAN:

        *MEAN* : float
            the mean of the result

        *VARIANCE* : float
            the variance of the result

        .. ENERGY:

        *ENERGY* : float
            the energy of the result, which is calculated using the `Stability
            Function <Function.Stability.function>` with the ``ENERGY`` metric

        .. ENTROPY:

        *ENTROPY* : float
            The entropy of the result, which is calculated using the `Stability
            Function <Function.Stability.function>` with the ENTROPY metric
            (Note: this is only present if the Mechanism's `function` is bounded
            between 0 and 1 (e.g. the `Logistic` Function)).
        """
    RESULT=RESULT
    MEAN=MEAN
    MEDIAN=MEDIAN
    STANDARD_DEVIATION=STANDARD_DEVIATION
    VARIANCE=VARIANCE
    ENERGY=ENERGY
    ENTROPY=ENTROPY
    # THIS WOULD HAVE BEEN NICE, BUT IDE DOESN'T EXECUTE IT, SO NAMES DON'T SHOW UP
    # for item in [item[NAME] for item in DDM_standard_output_states]:
    #     setattr(DDM_OUTPUT.__class__, item, item)


# IMPLEMENTATION NOTE:  IMPLEMENTS OFFSET PARAM BUT IT IS NOT CURRENTLY BEING USED
class RecurrentTransferMechanism(TransferMechanism):
    """
    RecurrentTransferMechanism(        \
    default_variable=None,             \
    size=None,                         \
    function=Linear,                   \
    matrix=HOLLOW_MATRIX,   \
    auto=None,                         \
    hetero=None,                       \
    initial_value=None,                \
    noise=0.0,                         \
    smoothing_factor=0.5,              \
    clip=[float:min, float:max],       \
    learning_rate=None,                \
    learning_function=Hebbian,         \
    integrator_mode=False,             \
    params=None,                       \
    name=None,                         \
    prefs=None)

    Subclass of `TransferMechanism` that implements a single-layer auto-recurrent network.

    COMMENT:
        Description
        -----------
            RecurrentTransferMechanism is a Subtype of the TransferMechanism Subtype of the ProcessingMechanisms Type
            of the Mechanism Category of the Component class.
            It implements a TransferMechanism with a recurrent projection (default matrix: HOLLOW_MATRIX).
            In all other respects, it is identical to a TransferMechanism.
    COMMENT

    Arguments
    ---------

    default_variable : number, list or np.ndarray : default Transfer_DEFAULT_BIAS
        specifies the input to the Mechanism to use if none is provided in a call to its
        `execute <Mechanism_Base.execute>` or `run <Mechanism_Base.run>` method;
        also serves as a template to specify the length of `variable <RecurrentTransferMechanism.variable>` for
        `function <RecurrentTransferMechanism.function>`, and the `primary OutputState <OutputState_Primary>`
        of the Mechanism.

    size : int, list or np.ndarray of ints
        specifies variable as array(s) of zeros if **variable** is not passed as an argument;
        if **variable** is specified, it takes precedence over the specification of **size**.
        As an example, the following mechanisms are equivalent::
            T1 = TransferMechanism(size = [3, 2])
            T2 = TransferMechanism(default_variable = [[0, 0, 0], [0, 0]])

    function : TransferFunction : default Linear
        specifies the function used to transform the input;  can be `Linear`, `Logistic`, `Exponential`,
        or a custom function.

    matrix : list, np.ndarray, np.matrix, matrix keyword, or AutoAssociativeProjection : default HOLLOW_MATRIX
        specifies the matrix to use for creating a `recurrent AutoAssociativeProjection <Recurrent_Transfer_Structure>`,
        or an AutoAssociativeProjection to use.

        - If **auto** and **matrix** are both specified, the diagonal terms are determined by auto and the off-diagonal
          terms are determined by matrix.

        - If **hetero** and **matrix** are both specified, the diagonal terms are determined by matrix and the
          off-diagonal terms are determined by hetero.

        - If **auto**, **hetero**, and **matrix** are all specified, matrix is ignored in favor of auto and hetero.

    auto : number, 1D array, or None : default None
        specifies matrix as a diagonal matrix with diagonal entries equal to **auto**, if **auto** is not None;
        If **auto** and **hetero** are both specified, then matrix is the sum of the two matrices from **auto** and
        **hetero**.

        In the following examples, assume that the default variable of the mechanism is length 4:

        - setting **auto** to 1 and **hetero** to -1 sets matrix to have a diagonal of
          1 and all non-diagonal entries -1:

            .. math::

                \\begin{bmatrix}
                    1 & -1 & -1 & -1 \\\\
                    -1 & 1 & -1 & -1 \\\\
                    -1 & -1 & 1 & -1 \\\\
                    -1 & -1 & -1 & 1 \\\\
                \\end{bmatrix}

        - setting **auto** to [1, 1, 2, 2] and **hetero** to -1 sets matrix to:

            .. math::

                \\begin{bmatrix}
                    1 & -1 & -1 & -1 \\\\
                    -1 & 1 & -1 & -1 \\\\
                    -1 & -1 & 2 & -1 \\\\
                    -1 & -1 & -1 & 2 \\\\
                \\end{bmatrix}

        - setting **auto** to [1, 1, 2, 2] and **hetero** to  [[3, 3, 3, 3], [3, 3, 3, 3], [4, 4, 4, 4], [4, 4, 4, 4]]
          sets matrix to:

            .. math::

                \\begin{bmatrix}
                    1 & 3 & 3 & 3 \\\\
                    3 & 1 & 3 & 3 \\\\
                    4 & 4 & 2 & 4 \\\\
                    4 & 4 & 4 & 2 \\\\
                \\end{bmatrix}

        See **matrix** for details on how **auto** and **hetero** may overwrite matrix.

        Can be modified by control.

    hetero : number, 2D array, or None : default None
        specifies matrix as a hollow matrix with all non-diagonal entries equal to **hetero**, if **hetero** is not None;
        If **auto** and **hetero** are both specified, then matrix is the sum of the two matrices from **auto** and
        **hetero**.

        When diagonal entries of **hetero** are specified with non-zero values, these entries are set to zero before
        hetero is used to produce a matrix.

        See **hetero** (above) for details on how various **auto** and **hetero** specifications are summed to produce a
        matrix.

        See **matrix** (above) for details on how **auto** and **hetero** may overwrite matrix.

        Can be modified by control.

    initial_value :  value, list or np.ndarray : default Transfer_DEFAULT_BIAS
        specifies the starting value for time-averaged input (only relevant if
        `integrator_mode <RecurrentTransferMechanism.integrator_mode>` is True).
        COMMENT:
            Transfer_DEFAULT_BIAS SHOULD RESOLVE TO A VALUE
        COMMENT

    noise : float or function : default 0.0
        a value added to the result of the `function <RecurrentTransferMechanism.function>` or to the result of
        `integrator_function <RecurrentTransferMechanism.integrator_function>`, depending on whether `integrator_mode
        <RecurrentTransferMechanism.integrator_mode>` is True or False. See `noise <RecurrentTransferMechanism.noise>`
        for more details.

    smoothing_factor : float : default 0.5
        the smoothing factor for exponential time averaging of input when `integrator_mode
        <RecurrentTransferMechanism.integrator_mode>` is set to True::

         result = (smoothing_factor * variable) +
         (1-smoothing_factor * input to mechanism's function on the previous time step)

    clip : list [float, float] : default None (Optional)
        specifies the allowable range for the result of `function <RecurrentTransferMechanism.function>` the item in
        index 0 specifies the minimum allowable value of the result, and the item in index 1 specifies the maximum
        allowable value; any element of the result that exceeds the specified minimum or maximum value is set to the
        value of `clip <RecurrentTransferMechanism.clip>` that it exceeds.


    enable_learning : boolean : default False
        specifies whether the Mechanism should be configured for learning;  if it is not (the default), then learning
        cannot be enabled until it is configured for learning by calling the Mechanism's `configure_learning
        <RecurrentTransferMechanism.configure_learning>` method.

    learning_rate : scalar, or list, 1d or 2d np.array, or np.matrix of numeric values: default False
        specifies the learning rate used by its `learning function <RecurrentTransferMechanism.learning_function>`.
        If it is `None`, the `default learning_rate for a LearningMechanism <LearningMechanism_Learning_Rate>` is
        used; if it is assigned a value, that is used as the learning_rate (see `learning_rate
        <RecurrentTransferMechanism.learning_rate>` for details).

    learning_function : function : default Hebbian
        specifies the function for the LearningMechanism if `learning has been specified
        <Recurrent_Transfer_Learning>` for the RecurrentTransferMechanism.  It can be any function so long as it
        takes a list or 1d array of numeric values as its `variable <Function_Base.variable>` and returns a sqaure
        matrix of numeric values with the same dimensions as the length of the input.

    params : Dict[param keyword: param value] : default None
        a `parameter dictionary <ParameterState_Specification>` that can be used to specify the parameters for
        the Mechanism, its function, and/or a custom function and its parameters.  Values specified for parameters in
        the dictionary override any assigned to those parameters in arguments of the constructor.

    name : str : default see `name <RecurrentTransferMechanism.name>`
        specifies the name of the RecurrentTransferMechanism.

    prefs : PreferenceSet or specification dict : default Mechanism.classPreferences
        specifies the `PreferenceSet` for the RecurrentTransferMechanism; see `prefs <RecurrentTransferMechanism.prefs>`
        for details.

    context : str : default componentType+INITIALIZING
        string used for contextualization of instantiation, hierarchical calls, executions, etc.

    Attributes
    ----------

    variable : value
        the input to Mechanism's `function <RecurrentTransferMechanism.variable>`.

    function : Function
        the Function used to transform the input.

    matrix : 2d np.array
        the `matrix <AutoAssociativeProjection.matrix>` parameter of the `recurrent_projection` for the Mechanism.

    recurrent_projection : AutoAssociativeProjection
        an `AutoAssociativeProjection` that projects from the Mechanism's `primary OutputState <OutputState_Primary>`
        back to its `primary inputState <Mechanism_InputStates>`.

    COMMENT:
       THE FOLLOWING IS THE CURRENT ASSIGNMENT
    COMMENT
    initial_value :  value, list or np.ndarray : Transfer_DEFAULT_BIAS
        determines the starting value for time-averaged input (only relevant if `smoothing_factor
        <RecurrentTransferMechanism.smoothing_factor>` parameter is not 1.0).
        COMMENT:
            Transfer_DEFAULT_BIAS SHOULD RESOLVE TO A VALUE
        COMMENT

    integrator_function:
        When *integrator_mode* is set to True, the RecurrentTransferMechanism executes its `integrator_function <RecurrentTransferMechanism.integrator_function>`,
        which is the `AdaptiveIntegrator`. See `AdaptiveIntegrator <AdaptiveIntegrator>` for more details on what it computes.
        Keep in mind that the `smoothing_factor <RecurrentTransferMechanism.smoothing_factor>` parameter of the `RecurrentTransferMechanism` corresponds to the
        `rate <RecurrentTransferMechanismIntegrator.rate>` of the `RecurrentTransferMechanismIntegrator`.

    integrator_mode:
        **When integrator_mode is set to True:**

        the variable of the mechanism is first passed into the following equation:

        .. math::
            value = previous\\_value(1-smoothing\\_factor) + variable \\cdot smoothing\\_factor + noise

        The result of the integrator function above is then passed into the `mechanism's function <RecurrentTransferMechanism.function>`. Note that
        on the first execution, *initial_value* sets previous_value.

        **When integrator_mode is set to False:**

        The variable of the mechanism is passed into the `function of the mechanism <RecurrentTransferMechanism.function>`. The mechanism's
        `integrator_function <RecurrentTransferMechanism.integrator_function>` is skipped entirely, and all related arguments (*noise*, *leak*,
        *initial_value*, and *time_step_size*) are ignored.

    noise : float or function : default 0.0
        When `integrator_mode <RecurrentTransferMechanism.integrator_mode>` is set to True, noise is passed into the
        `integrator_function <RecurrentTransferMechanism.integrator_function>`. Otherwise, noise is added to the output
        of the `function <RecurrentTransferMechanism.function>`.

        If noise is a list or array, it must be the same length as `variable
        <RecurrentTransferMechanism.default_variable>`.

        If noise is specified as a single float or function, while `variable <RecurrentTransferMechanism.variable>` is a
        list or array, noise will be applied to each variable element. In the case of a noise function, this means that
        the function will be executed separately for each variable element.

        .. note::
            In order to generate random noise, we recommend selecting a probability distribution function
            (see `Distribution Functions <DistributionFunction>` for details), which will generate a new noise value from
            its distribution on each execution. If noise is specified as a float or as a function with a fixed output, then
            the noise will simply be an offset that remains the same across all executions.

    smoothing_factor : float : default 0.5
        the smoothing factor for exponential time averaging of input when `integrator_mode
        <RecurrentTransferMechanism.integrator_mode>` is set to True::

          result = (smoothing_factor * current input) + (1-smoothing_factor * result on previous time_step)

    clip : list [float, float] : default None (Optional)
        specifies the allowable range for the result of `function <RecurrentTransferMechanism.function>`

        the item in index 0 specifies the minimum allowable value of the result, and the item in index 1 specifies the
        maximum allowable value; any element of the result that exceeds the specified minimum or maximum value is set to
         the value of `clip <RecurrentTransferMechanism.clip>` that it exceeds.

    previous_input : 1d np.array of floats
        the value of the input on the previous execution, including the value of `recurrent_projection`.

    learning_enabled : bool : default False
        indicates whether learning has been enabled for the RecurrentTransferMechanism.  It is set to `True` if
        `learning is specified <Recurrent_Transfer_Learning>` at the time of construction (i.e., if the
        **enable_learning** argument of the Mechanism's constructor is assigned `True`, or when it is configured for
        learning using the `configure_learning <RecurrentTransferMechanism.configure_learning>` method.  Once learning
        has been configured, `learning_enabled <RecurrentMechahinsm.learning_enabled>` can be toggled at any time to
        enable or disable learning; however, if the Mechanism has not been configured for learning, an attempt to
        set `learning_enabled <RecurrentMechahinsm.learning_enabled>` to `True` elicits a warning and is then
        ignored.

    learning_rate : float, 1d or 2d np.array, or np.matrix of numeric values : default None
        specifies the learning rate used by the `learning_function <RecurrentTransferMechanism.learning_function>`
        of the `learning_mechanism <RecurrentTransferMechanism.learning_mechanism>` (see `learning_rate
        <AutoAssociativeLearningMechanism.learning_rate>` for details concerning specification and default value
        assignement).

    learning_function : function : default Hebbian
        the function used by the `learning_mechanism <RecurrentTransferMechanism.learning_mechanism>` to train the
        `recurrent_projection <RecurrentTransferMechanism.recurrent_projection>` if `learning is specified
        <Recurrent_Transfer_Learning>`.

    learning_mechanism : LearningMechanism
        created automatically if `learning is specified <Recurrent_Transfer_Learning>`, and used to train the
        `recurrent_projection <RecurrentTransferMechanism.recurrent_projection>`.

    value : 2d np.array [array(float64)]
        result of executing `function <RecurrentTransferMechanism.function>`; same value as first item of
        `output_values <RecurrentTransferMechanism.output_values>`.

    COMMENT:
        CORRECTED:
        value : 1d np.array
            the output of ``function``;  also assigned to ``value`` of the TRANSFER_RESULT OutputState
            and the first item of ``output_values``.
    COMMENT

    output_states : Dict[str: OutputState]
        an OrderedDict with the following `OutputStates <OutputState>`:

        * `TRANSFER_RESULT`, the :keyword:`value` of which is the **result** of `function <RecurrentTransferMechanism.function>`;
        * `TRANSFER_MEAN`, the :keyword:`value` of which is the mean of the result;
        * `TRANSFER_VARIANCE`, the :keyword:`value` of which is the variance of the result;
        * `ENERGY`, the :keyword:`value` of which is the energy of the result,
          calculated using the `Stability` Function with the ENERGY metric;
        * `ENTROPY`, the :keyword:`value` of which is the entropy of the result,
          calculated using the `Stability` Function with the ENTROPY metric;
          note:  this is only present if the Mechanism's :keyword:`function` is bounded between 0 and 1
          (e.g., the `Logistic` function).

    output_values : List[array(float64), float, float]
        a list with the following items:

        * **result** of the ``function`` calculation (value of TRANSFER_RESULT OutputState);
        * **mean** of the result (``value`` of TRANSFER_MEAN OutputState)
        * **variance** of the result (``value`` of TRANSFER_VARIANCE OutputState);
        * **energy** of the result (``value`` of ENERGY OutputState);
        * **entropy** of the result (if the ENTROPY OutputState is present).

    name : str
        the name of the RecurrentTransferMechanism; if it is not specified in the **name** argument of the constructor,
        a default is assigned by MechanismRegistry (see `Naming` for conventions used for default and duplicate names).

    prefs : PreferenceSet or specification dict
        the `PreferenceSet` for the RecurrentTransferMechanism; if it is not specified in the **prefs** argument of the
        constructor, a default is assigned using `classPreferences` defined in __init__.py (see :doc:`PreferenceSet
        <LINK>` for details).


    Returns
    -------
    instance of RecurrentTransferMechanism : RecurrentTransferMechanism

    """
    componentType = RECURRENT_TRANSFER_MECHANISM

    class ClassDefaults(TransferMechanism.ClassDefaults):
        variable = np.array([[0]])

    paramClassDefaults = TransferMechanism.paramClassDefaults.copy()

    standard_output_states = TransferMechanism.standard_output_states.copy()
    standard_output_states.extend([{NAME:ENERGY}, {NAME:ENTROPY}])

    @tc.typecheck
    def __init__(self,
                 default_variable=None,
                 size=None,
                 function=Linear,
                 matrix=HOLLOW_MATRIX,
                 auto=None,
                 hetero=None,
                 initial_value=None,
                 noise=0.0,
                 smoothing_factor: is_numeric_or_none=0.5,
                 integrator_mode=False,
                 clip=None,
                 input_states:tc.optional(tc.any(list, dict)) = None,
                 enable_learning:bool=False,
                 learning_rate:tc.optional(tc.any(parameter_spec, bool))=None,
                 learning_function: tc.any(is_function_type) = Hebbian,
                 output_states:tc.optional(tc.any(str, Iterable))=RESULT,
                 params=None,
                 name=None,
                 prefs: is_pref_set=None):
        """Instantiate RecurrentTransferMechanism
        """

        # Default output_states is specified in constructor as a string rather than a list
        # to avoid "gotcha" associated with mutable default arguments
        # (see: bit.ly/2uID3s3 and http://docs.python-guide.org/en/latest/writing/gotchas/)
        if output_states is None or output_states is RESULT:
            output_states = [RESULT]

        if isinstance(hetero, (list, np.matrix)):
            hetero = np.array(hetero)

        self._learning_enabled = enable_learning

        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(input_states=input_states,
                                                  initial_value=initial_value,
                                                  matrix=matrix,
                                                  integrator_mode=integrator_mode,
                                                  learning_rate=learning_rate,
                                                  learning_function=learning_function,
                                                  output_states=output_states,
                                                  params=params,
                                                  noise=noise,
                                                  auto=auto,
                                                  hetero=hetero)

        if not isinstance(self.standard_output_states, StandardOutputStates):
            self.standard_output_states = StandardOutputStates(self,
                                                               self.standard_output_states,
                                                               indices=PRIMARY)

        super().__init__(default_variable=default_variable,
                         size=size,
                         input_states=input_states,
                         function=function,
                         initial_value=initial_value,
                         noise=noise,
                         integrator_mode=integrator_mode,
                         smoothing_factor=smoothing_factor,
                         clip=clip,
                         output_states=output_states,
                         params=params,
                         name=name,
                         prefs=prefs)

    def _validate_params(self, request_set, target_set=None, context=None):
        """Validate shape and size of auto, hetero, matrix.
        """
        from psyneulink.library.projections.pathway.autoassociativeprojection import AutoAssociativeProjection

        super()._validate_params(request_set=request_set, target_set=target_set, context=context)

        if AUTO in target_set:
            auto_param = target_set[AUTO]
            if (auto_param is not None) and not isinstance(auto_param, (np.ndarray, list, numbers.Number)):
                raise RecurrentTransferError("auto parameter ({}) of {} is of incompatible type: it should be a "
                                             "number, None, or a 1D numeric array".format(auto_param, self))
            if isinstance(auto_param, (np.ndarray, list)) and len(auto_param) != 1 and len(auto_param) != self.size[0]:
                raise RecurrentTransferError("auto parameter ({0}) for {1} is of incompatible length with the size "
                                             "({2}) of its owner, {1}.".format(auto_param, self, self.size[0]))

        if HETERO in target_set:
            hetero_param = target_set[HETERO]
            if hetero_param is not None and not isinstance(hetero_param, (np.matrix, np.ndarray, list, numbers.Number)):
                raise RecurrentTransferError("hetero parameter ({}) of {} is of incompatible type: it should be a "
                                             "number, None, or a 2D numeric matrix or array".format(hetero_param, self))
            hetero_shape = np.array(hetero_param).shape
            if hetero_shape != (1,) and hetero_shape != (1, 1):
                if isinstance(hetero_param, (np.ndarray, list, np.matrix)) and hetero_shape[0] != self.size[0]:
                    raise RecurrentTransferError("hetero parameter ({0}) for {1} is of incompatible size with the size "
                                                 "({2}) of its owner, {1}.".format(hetero_param, self, self.size[0]))
                if isinstance(hetero_param, (np.ndarray, list, np.matrix)) and hetero_shape[0] != hetero_shape[1]:
                    raise RecurrentTransferError("hetero parameter ({}) for {} must be square.".format(hetero_param, self))

        # Validate MATRIX
        if MATRIX in target_set:

            matrix_param = target_set[MATRIX]
            size = self.size[0]

            if isinstance(matrix_param, AutoAssociativeProjection):
                matrix = matrix_param.matrix

            elif isinstance(matrix_param, str):
                matrix = get_matrix(matrix_param, size, size)

            elif isinstance(matrix_param, (np.matrix, list)):
                matrix = np.array(matrix_param)

            else:
                matrix = matrix_param
            if matrix is None:
                rows = cols = size # this is a hack just to skip the tests ahead: if the matrix really is None, that is
                # checked up ahead, in _instantiate_attributes_before_function()
            else:
                rows = np.array(matrix).shape[0]
                cols = np.array(matrix).shape[1]

            # Shape of matrix must be square
            if rows != cols:
                if isinstance(matrix_param, AutoAssociativeProjection):
                    # if __name__ == '__main__':
                    err_msg = ("{} param of {} must be square to be used as recurrent projection for {}".
                               format(MATRIX, matrix_param.name, self.name))
                else:
                    err_msg = "{0} param for {1} must be square; currently, the {0} param is: {2}".\
                        format(MATRIX, self.name, matrix)
                raise RecurrentTransferError(err_msg)

            # Size of matrix must equal length of variable:
            if rows != size:
                if (matrix_param, AutoAssociativeProjection):
                    # if __name__ == '__main__':
                    err_msg = ("Number of rows in {} param for {} ({}) must be same as the size of variable for "
                               "{} {} (whose size is {} and whose variable is {})".
                               format(MATRIX, self.name, rows, self.__class__.__name__, self.name, self.size, self.instance_defaults.variable))
                else:
                    err_msg = ("Size of {} param for {} ({}) must be the same as its variable ({})".
                               format(MATRIX, self.name, rows, size))
                raise RecurrentTransferError(err_msg)

        # Validate DECAY
        # if DECAY in target_set and target_set[DECAY] is not None:
        #
        #     decay = target_set[DECAY]
        #     if not (0.0 <= decay and decay <= 1.0):
        #         raise RecurrentTransferError("{} argument for {} ({}) must be from 0.0 to 1.0".
        #                                      format(DECAY, self.name, decay))

        # FIX: validate learning_function and learning_rate here (use Hebbian as template for learning_rate

    def _instantiate_attributes_before_function(self, function=None, context=None):
        """ using the `matrix` argument the user passed in (which is now stored in function_params), instantiate
        ParameterStates for auto and hetero if they haven't already been instantiated. This is useful if auto and
        hetero were None in the initialization call.
        :param function:
        """
        super()._instantiate_attributes_before_function(function=function, context=context)

        param_keys = self._parameter_states.key_values
        specified_matrix = get_matrix(self.params[MATRIX], self.size[0], self.size[0])

        # 9/23/17 JDC: DOESN'T matrix arg default to something?
        # If no matrix was specified, then both AUTO and HETERO must be specified
        if specified_matrix is None and (AUTO not in param_keys or HETERO not in param_keys):
            raise RecurrentTransferError("Matrix parameter ({}) for {} failed to produce a suitable matrix: "
                                         "if the matrix parameter does not produce a suitable matrix, the "
                                         "'auto' and 'hetero' parameters must be specified; currently, either"
                                         "auto or hetero parameter is missing.".format(self.params[MATRIX], self))

        # # MODIFIED 9/23/17 OLD:
        # if AUTO not in param_keys:
        # MODIFIED 9/23/17 NEW [JDC]:
        # if self.auto is not None:
        if AUTO not in param_keys and HETERO in param_keys:
        # MODIFIED 9/23/17 END
            d = np.diagonal(specified_matrix).copy()
            state = _instantiate_state(owner=self,
                                       state_type=ParameterState,
                                       name=AUTO,
                                       reference_value=d,
                                       reference_value_name=AUTO,
                                       params=None,
                                       context=context)
            self.auto = d
            if state is not None:
                self._parameter_states[AUTO] = state
            else:
                raise RecurrentTransferError("Failed to create ParameterState for `auto` attribute for {} \"{}\"".
                                           format(self.__class__.__name__, self.name))
        # # MODIFIED 9/23/17 OLD:
        # if HETERO not in param_keys:
        # MODIFIED 9/23/17 NEW [JDC]:
        # if self.hetero is not None:

        if HETERO not in param_keys and AUTO in param_keys:
        # MODIFIED 9/23/17 END

            m = specified_matrix.copy()
            np.fill_diagonal(m, 0.0)
            self.hetero = m
            state = _instantiate_state(owner=self,
                                       state_type=ParameterState,
                                       name=HETERO,
                                       reference_value=m,
                                       reference_value_name=HETERO,
                                       params=None,
                                       context=context)
            if state is not None:
                self._parameter_states[HETERO] = state
            else:
                raise RecurrentTransferError("Failed to create ParameterState for `hetero` attribute for {} \"{}\"".
                                           format(self.__class__.__name__, self.name))
    def _instantiate_attributes_after_function(self, context=None):
        """Instantiate recurrent_projection, matrix, and the functions for the ENERGY and ENTROPY OutputStates
        """
        from psyneulink.library.projections.pathway.autoassociativeprojection import AutoAssociativeProjection

        super()._instantiate_attributes_after_function(context=context)


        # [9/23/17 JDC: WHY IS THIS GETTING DONE HERE RATHER THAN IN _instantiate_attributes_before_function ??]

        if self.auto is None and self.hetero is None:
            self.matrix = get_matrix(self.params[MATRIX], self.size[0], self.size[0])
            if self.matrix is None:
                raise RecurrentTransferError("PROGRAM ERROR: Failed to instantiate \'matrix\' param for {}".
                                             format(self.__class__.__name__))

        # (7/19/17 CW) this line of code is now questionable, given the changes to matrix and the recurrent projection
        if isinstance(self.matrix, AutoAssociativeProjection):
            self.recurrent_projection = self.matrix

        # IMPLEMENTATION NOTE:  THESE SHOULD BE MOVED TO COMPOSITION WHEN THAT IS IMPLEMENTED
        else:
            self.recurrent_projection = self._instantiate_recurrent_projection(self,
                                                                               matrix=self.matrix,
                                                                               context=context)

        if self.learning_enabled:
            self.configure_learning(context=context)

        if ENERGY in self.output_states.names:
            energy = Stability(self.instance_defaults.variable[0],
                               metric=ENERGY,
                               transfer_fct=self.function,
                               matrix=self.recurrent_projection._parameter_states[MATRIX])
            self.output_states[ENERGY]._calculate = energy.function

        if ENTROPY in self.output_states.names:
            if self.function_object.bounds == (0,1) or self.clip == (0,1):
                entropy = Stability(self.instance_defaults.variable[0],
                                    metric=ENTROPY,
                                    transfer_fct=self.function,
                                    matrix=self.recurrent_projection._parameter_states[MATRIX])
                self.output_states[ENTROPY]._calculate = entropy.function
            else:
                del self.output_states[ENTROPY]

    def _update_parameter_states(self, runtime_params=None, context=None):
        for state in self._parameter_states:
            # (8/2/17 CW) because the auto and hetero params are solely used by the AutoAssociativeProjection
            # (the RecurrentTransferMechanism doesn't use them), the auto and hetero param states are updated in the
            # projection's _update_parameter_states, and accordingly are not updated here
            if state.name != AUTO or state.name != HETERO:
                state.update(params=runtime_params, context=context)

    # 8/2/17 CW: this property is not optimal for performance: if we want to optimize performance we should create a
    # single flag to check whether to get matrix from auto and hetero?
    @property
    def matrix(self):
        from psyneulink.library.projections.pathway.autoassociativeprojection import get_auto_matrix, get_hetero_matrix

        if hasattr(self, '_parameter_states') \
                and 'auto' in self._parameter_states and 'hetero' in self._parameter_states:
            if not hasattr(self, 'size'):
                raise Exception('Error in retrieving matrix parameter for {}: `size` is not instantiated.'.format(self))
            a = get_auto_matrix(self.auto, self.size[0])
            c = get_hetero_matrix(self.hetero, self.size[0])
            return a + c
        else:
            # if auto and hetero are not yet instantiated, then just use the standard method of attribute retrieval
            backing_field = '_matrix'
            # try:
            #     return self.recurrent_projection.matrix
            # except (AttributeError, TypeError):
            # KAM MODIFIED 1/9/18 -- removed parameter state value look up (now reserved for 'mod_' params)
            return getattr(self, backing_field)

    @matrix.setter
    def matrix(self, val): # simplified version of standard setter (in Component.py)
        if hasattr(self, "recurrent_projection"):
            self.recurrent_projection.parameter_states["matrix"].function_object.previous_value = val
        if hasattr(self, '_parameter_states')\
                and 'auto' in self._parameter_states and 'hetero' in self._parameter_states:
            if hasattr(self, 'size'):
                val = get_matrix(val, self.size[0], self.size[0])
            temp_matrix = val.copy()
            self.auto = np.diag(temp_matrix).copy()
            np.fill_diagonal(temp_matrix, 0)
            self.hetero = temp_matrix
        else:
            name = 'matrix'
            backing_field = '_matrix'
            if self.paramValidationPref and hasattr(self, PARAMS_CURRENT):
                self._assign_params(request_set={name: val}, context=ContextFlags.PROPERTY)
            else:
                setattr(self, backing_field, val)
            self.user_params.__additem__(name, val)

            if hasattr(self, '_parameter_states') and name in self._parameter_states:
                param_state = self._parameter_states[name]

                if hasattr(param_state.function_object, 'initializer'):
                    param_state.function_object.reinitialize = val

    @property
    def auto(self):
        return getattr(self, "_auto")

    @auto.setter
    def auto(self, val):

        if self.paramValidationPref and hasattr(self, PARAMS_CURRENT):
            self._assign_params(request_set={"auto": val}, context=ContextFlags.PROPERTY)
        else:
            setattr(self, "_auto", val)

        if hasattr(self, "recurrent_projection") and 'hetero' in self._parameter_states:
            self.recurrent_projection.parameter_states["matrix"].function_object.previous_value = self.matrix

        # Update user_params dict with new value
        self.user_params.__additem__("auto", val)

    @property
    def hetero(self):
        return getattr(self, "_hetero")

    @hetero.setter
    def hetero(self, val):

        if self.paramValidationPref and hasattr(self, PARAMS_CURRENT):
            self._assign_params(request_set={"hetero": val}, context=ContextFlags.PROPERTY)
        else:
            setattr(self, "_hetero", val)

        if hasattr(self, "recurrent_projection") and 'auto' in self._parameter_states:
            self.recurrent_projection.parameter_states["matrix"].function_object.previous_value = self.matrix

        # Update user_params dict with new value
        self.user_params.__additem__("hetero", val)
    @property
    def learning_enabled(self):
        return self._learning_enabled

    @learning_enabled.setter
    def learning_enabled(self, value:bool):

        self._learning_enabled = value
        # Enable learning for RecurrentTransferMechanism's learning_mechanism
        if hasattr(self, 'learning_mechanism'):
            self.learning_mechanism.learning_enabled = value
        # If RecurrentTransferMechanism has no LearningMechanism, warn and then ignore attempt to set learning_enabled
        elif value is True:
            print("Learning cannot be enabled for {} because it has no {}".
                  format(self.name, LearningMechanism.__name__))
            return

    # IMPLEMENTATION NOTE:  THIS SHOULD BE MOVED TO COMPOSITION ONCE THAT IS IMPLEMENTED
    @tc.typecheck
    def _instantiate_recurrent_projection(self,
                                          mech: Mechanism_Base,
                                          # this typecheck was failing, I didn't want to fix (7/19/17 CW)
                                          # matrix:is_matrix=HOLLOW_MATRIX,
                                          matrix=HOLLOW_MATRIX,
                                          context=None):
        """Instantiate a AutoAssociativeProjection from Mechanism to itself

        """

        from psyneulink.library.projections.pathway.autoassociativeprojection import AutoAssociativeProjection

        if isinstance(matrix, str):
            size = len(mech.instance_defaults.variable[0])
            matrix = get_matrix(matrix, size, size)

        # IMPLEMENTATION NOTE: THIS SHOULD BE MOVED TO COMPOSITION WHEN THAT IS IMPLEMENTED
        return AutoAssociativeProjection(owner=mech,
                                         matrix=matrix,
                                         name=mech.name + ' recurrent projection')

    # IMPLEMENTATION NOTE: THIS SHOULD BE MOVED TO COMPOSITION WHEN THAT IS IMPLEMENTED
    def _instantiate_learning_mechanism(self,
                                        activity_vector:tc.any(list, np.array),
                                        learning_function:tc.any(is_function_type),
                                        learning_rate:tc.any(numbers.Number, list, np.ndarray, np.matrix),
                                        matrix,
                                        context=None):

        learning_mechanism = AutoAssociativeLearningMechanism(default_variable=[activity_vector.value],
                                                              # learning_signals=[self.recurrent_projection],
                                                              function=learning_function,
                                                              learning_rate=learning_rate,
                                                              name="{} for {}".format(
                                                                      AutoAssociativeLearningMechanism.className,
                                                                      self.name))

        # Instantiate Projection from Mechanism's output to LearningMechanism
        MappingProjection(sender=activity_vector,
                          receiver=learning_mechanism.input_states[ACTIVATION_INPUT],
                          name="Error Projection for {}".format(learning_mechanism.name))

        # Instantiate Projection from LearningMechanism to Mechanism's AutoAssociativeProjection
        LearningProjection(sender=learning_mechanism.output_states[LEARNING_SIGNAL],
                           receiver=matrix.parameter_states[MATRIX],
                           name="{} for {}".format(LearningProjection.className, self.recurrent_projection.name))

        return learning_mechanism

    def configure_learning(self, learning_function=None, learning_rate=None, context=None):
        """
        configure_learning(learning_function=None, learning_rate=None)

        Configure RecurrentTransferMechanism for learning. Creates the following Components:

        * an `AutoAssociativeLearningMechanism` -- if the **learning_function** and/or **learning_rate** arguments are
          specified, they are used to construct the LearningMechanism, otherwise the values specified in the
          RecurrentTransferMechanism's constructor are used;
        ..
        * a `MappingProjection` from the RecurrentTransferMechanism's `primary OutputState <OutputState_Primary>`
          to the AutoAssociativeLearningMechanism's *ACTIVATION_INPUT* InputState;
        ..
        * a `LearningProjection` from the AutoAssociativeLearningMechanism's *LEARNING_SIGNAL* OutputState to
          the RecurrentTransferMechanism's `recurrent_projection <RecurrentTransferMechanism.recurrent_projection>`.

        """

        # This insures that these are validated if the method is called from the command line (i.e., by the user)
        if learning_function:
            self.learning_function = learning_function
        if learning_rate:
            self.learning_rate = learning_rate

        context = context or ContextFlags.COMMAND_LINE
        self.context.source = self.context.source or ContextFlags.COMMAND_LINE

        self.learning_mechanism = self._instantiate_learning_mechanism(activity_vector=self.output_state,
                                                                       learning_function=self.learning_function,
                                                                       learning_rate=self.learning_rate,
                                                                       matrix=self.recurrent_projection,
                                                                       context=context)
        if self.learning_mechanism is None:
            self.learning_enabled = False
