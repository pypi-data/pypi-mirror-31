# Princeton University licenses this file to You under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.  You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


# **************************************  LCControlMechanism ************************************************

"""

Overview
--------

An LCControlMechanism is a `ControlMechanism <ControlMechanism>` that multiplicatively modulates the `function
<Mechanism_Base.function>` of one or more `Mechanisms <Mechanism>` (usually `TransferMechanisms <TransferMechanism>`).
It implements an abstract model of the `locus coeruleus (LC)  <https://www.ncbi.nlm.nih.gov/pubmed/12371518>`_ that
uses an `FHNIntegrator` Function to generate its output.  This is modulated by a `mode <LCControlMechanism.mode_FHN>`
parameter that regulates its functioning between `"tonic" and "phasic" modes of operation
<LCControlMechanism_Modes_Of_Operation>`.  The Mechanisms modulated by an LCControlMechanism can be listed using
its `show <LCControlMechanism.show>` method.  When used with an `AGTControlMechanism` to regulate the `mode
<FHNIntegrator.mode>` parameter of its `FHNIntegrator` Function, it implements a form of the `Adaptive Gain Theory
<http://www.annualreviews.org/doi/abs/10.1146/annurev.neuro.28.061604.135709>`_ of the locus coeruleus-norepinephrine
(LC-NE) system.

.. _LCControlMechanism_Creation:

Creating an LCControlMechanism
-----------------------

An LCControlMechanism can be created in any of the ways used to `create a ControlMechanism <ControlMechanism_Creation>`.
The following sections describe how to specify the inputs that drive the LCControlMechanism's response, and the
Mechanisms that it controls.


.. _LCControlMechanism_ObjectiveMechanism:

ObjectiveMechanism and Monitored OutputStates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like all ControlMechanisms, an LCControlMechanism receives its `input <LCControlMechanism_Input>` from an
`ObjectiveMechanism` that, in turn, receives its input from a specified list of `OutputStates <OutputState>`.  These
are used to drive the `phasic response <LCControlMechanism_Modes_Of_Operation>` of the LCControlMechanism.  The
ObjectiveMechanism and/or the OutputStates from which it gets its input can be `specified in the standard way for a
ControlMechanism <ControlMechanism_ObjectiveMechanism>`).  By default, an LCControlMechanism creates an
ObjectiveMechanism that uses a `CombineMeans` Function to sum the means of the `value <OutputState.value>`\\s of the
OutputStates from which it gets its input.  However, this can be customized by specifying a different
ObjectiveMechanism or its `function <ObjectiveMechanism.function>`, so long as these generate a result that is a
scalar value.

.. _LCControlMechanism_Modulated_Mechanisms:

Specifying Mechanisms to Modulate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Mechanisms to be modulated by an LCControlMechanism are specified in its **modulated_mechanisms** argument. An
LCControlMechanism controls a `Mechanism <Mechanism>` by modifying the `multiplicative_param
<Function_Modulatory_Params>` of the Mechanism's `function <TransferMechanism.function>`.  Therefore, any Mechanism
specified for control by an LCControlMechanism must be either a `TransferMechanism`, or a Mechanism that uses a
`TransferFunction` or a class of `Function <Function>` that implements a `multiplicative_param
<Function_Modulatory_Params>`.  The **modulate_mechanisms** argument must be a list of such Mechanisms.  The keyword
*ALL* can also be used to specify all of the eligible `ProcessMechanisms <ProcessingMechanism>` in all of the
`Compositions <Composition>` to which the LCControlMechanism belongs.  If a Mechanism specified in the
**modulated_mechanisms** argument does not implement a multiplicative_param, it is ignored. A `ControlProjection` is
automatically created that projects from the LCControlMechanism to the `ParameterState` for the `multiplicative_param
<Function_Modulatory_Params>` of every Mechanism specified in the **modulated_mechanisms** argument (and listed in
its `modulated_mechanisms <LCControlMechanism.modulated_mechanisms>` attribute).

.. _LCControlMechanism_Structure:

Structure
---------

.. _LCControlMechanism_Input:

Input
~~~~~

COMMENT:

An LCControlMechanism has a single (primary) `InputState <InputState_Primary>` that receives its input via a
`MappingProjection` from the *OUTCOME* `OutputState <ObjectiveMechanism_Output>` of an `ObjectiveMechanism`.
The Objective Mechanism is specified in the **objective_mechanism** argument of its constructor, and listed in its
`objective_mechanism <EVCControlMechanism.objective_mechanism>` attribute.  The OutputStates monitored by the
ObjectiveMechanism (listed in its `monitored_output_states <ObjectiveMechanism.monitored_output_states>`
attribute) are also listed in the `monitored_output_states <ControlMechanism.monitored_output_states>`
of the ControlMechanism (see `ControlMechanism_ObjectiveMechanism` for how the ObjectiveMechanism and the
OutputStates it monitors are specified).  The OutputStates monitored by the ControlMechanism's `objective_mechanism
<ControlMechanism.objective_mechanism>` can be displayed using its `show <ControlMechanism.show>` method.
The ObjectiveMechanism's `function <ObjectiveMechanism>` evaluates the specified OutputStates, and the result is
conveyed as the input to the ControlMechanism.


Projections from any Mechanisms
specified in the **input_states** argument of the LCControlMechanism's constructor;  its `value <InputState.value>` is a
scalar, so the `matrix <MappingProjection.matrix>` parameter for any MappingProjection to the LCControlMechanism's InputState
from an OutputStates with a `value <OutputState.value>` that is an array of greater than length 1 is assigned a
`FULL_CONNECTIVITY_MATRIX`.  The `value <InputState.value>` of the LCControlMechanism's InputState is used as the `variable
<FHNIntegrator.variable>` for the LCControlMechanism's `function <LCControlMechanism.function>`.


.. _LCControlMechanism_ObjectiveMechanism

   By default, the ObjectiveMechanism is assigned a CombineMeans Function that takes the mean of the `value
   <InputState.value>` received from each OutputState specified in **monitored_output_states** (i.e., of each of its
   `input_states <ObjectiveMechanism.input_states>`) and sums these; the result is provided as the input to the LCControlMechanism.
   The contribution of each monitored_output_state can be weighted and/or exponentitaed in the standard way for the
       monitored_output_states/input_states of an ObjectiveMechanism

FROM CONTROL_MECHANISM:
A ControlMechanism has a single *ERROR_SIGNAL* `InputState`, the `value <InputState.value>` of which is used as the
input to the ControlMechanism's `function <ControlMechanism.function>`, that determines the ControlMechanism's
`allocation_policy <ControlMechanism.allocation_policy>`. The *ERROR_SIGNAL* InputState receives its input
via a `MappingProjection` from the *OUTCOME* `OutputState <ObjectiveMechanism_Output>` of an `ObjectiveMechanism`.
The Objective Mechanism is specified in the **objective_mechanism** argument of its constructor, and listed in its
`objective_mechanism <EVCControlMechanism.objective_mechanism>` attribute.  The OutputStates monitored by the
ObjectiveMechanism (listed in its `monitored_output_states <ObjectiveMechanism.monitored_output_states>`
attribute) are also listed in the `monitored_output_states <ControlMechanism.monitored_output_states>`
of the ControlMechanism (see `ControlMechanism_ObjectiveMechanism` for how the ObjectiveMechanism and the
OutputStates it monitors are specified).  The OutputStates monitored by the ControlMechanism's `objective_mechanism
<ControlMechanism.objective_mechanism>` can be displayed using its `show <ControlMechanism.show>` method.
The ObjectiveMechanism's `function <ObjectiveMechanism>` evaluates the specified OutputStates, and the result is
conveyed as the input to the ControlMechanism.

COMMENT

.. _LCControlMechanism_ObjectiveMechanism:

ObjectiveMechanism
^^^^^^^^^^^^^^^^^^

Like any ControlMechanism, an LCControlMechanism receives its input from the *OUTCOME* `OutputState
<ObjectiveMechanism_Output>` of an `ObjectiveMechanism`, via a MappingProjection to its `primary InputState
<InputStatePrimary>`.  The ObjectiveFunction is listed in the LCControlMechanism's `objective_mechanism
<LCControlMechanism.objective_mechanism>` attribute.  By default, the ObjectiveMechanism's function is a `CombineMeans`
function with its default `operation <LinearCombination.operation>` of *SUM*; this takes the mean of the `value
<OutputState.value>` of each of the OutputStates that it monitors (listed in its `monitored_output_states
<ObjectiveMechanism.monitored_output_states>` attribute, and returns the sum of those means.  However, this can be
customized in a variety of ways:

    * by specifying a different `function <ObjectiveMechanism.function>` for the ObjectiveMechanism
      (see `ObjectiveMechanism_Weights_and_Exponents_Example` for an example);
    ..
    * using a list to specify the OutputStates to be monitored  (and the `tuples format
      <InputState_Tuple_Specification>` to specify weights and/or exponents for them) in the
      **objective_mechanism** argument of the EVCControlMechanism's constructor;
    ..
    * using the  **monitored_output_states** argument of the `objective_mechanism <LCControlMechanism.objective_mechanism>`'s
      constructor;
    ..
    * specifying a different `ObjectiveMechanism` in the LCControlMechanism's **objective_mechanism** argument of the
      EVCControlMechanism's constructor. The result of the `objective_mechanism <LCControlMechanism.objective_mechanism>`'s
      `function <ObjectiveMechanism.function>` is used as the input to the LCControlMechanism.

    .. _LCControlMechanism_Objective_Mechanism_Function_Note:

    .. note::
       If a constructor for an `ObjectiveMechanism` is used for the **objective_mechanism** argument of the
       LCControlMechanism's constructor, then the default values of its attributes override any used by the LCControlMechanism
       for its `objective_mechanism <EVCControlMechanism.objective_mechanism>`.  In particular, whereas an ObjectiveMechanism
       uses `LinearCombination` as the default for its `function <ObjectiveMechanism.function>`, an LCControlMechanism
       typically uses `CombineMeans` for the `function <ObjectiveMechanism.function>` of its `objective_mechanism
       <LCControlMechanism.objective_mechanism>`.  As a consequence, if the constructor for an ObjectiveMechanism is used to
       specify the LCControlMechanism's **objective_mechanism** argument, and the **function** argument is not specified,
       `LinearCombination` rather than `CombineMeans` will be used for the ObjectiveMechanism's `function
       <ObjectiveMechanism.function>`.  To insure that `CombineMeans` is used, it must be specified explicitly in the
       **function** argument of the constructor for the ObjectiveMechanism (for an example of a similar condition
       for an EVCControlMechanism see 1st example under `System_Control_Examples`).

The OutputStates monitored by the LC's ObjectiveMechanism are listed in its `monitored_output_states
<ObjectiveMechanism.monitored_output_states>` attribute), as well as in the `monitored_output_states
<LCControlMechanism.monitored_output_states>` attribute of the LCControlMechanism itself.  These can be displayed using the
LCControlMechanism's `show <LCControlMechanism.show>` method.

.. _LCControlMechanism_Function:

Function
~~~~~~~~

COMMENT:
XXX ADD MENTION OF allocation_policy HERE
COMMENT

An LCControlMechanism uses the `FHNIntegrator` as its `function <LCControlMechanism.function`; this implements a `FitzHugh-Nagumo
model <https://en.wikipedia.org/wiki/FitzHugh–Nagumo_model>`_ often used to describe the spiking of a neuron,
but in this case the population activity of the LC (see `Gilzenrat et al., 2002
<http://www.sciencedirect.com/science/article/pii/S0893608002000552?via%3Dihub>`_). The `FHNIntegrator` Function
takes the `input <LCControlMechanism_Input>` to the LCControlMechanism as its `variable <FHNIntegrator.variable>`. All
of the `FHNIntegrator` function parameters are exposed on the LCControlMechanism.

.. _LCControlMechanism_Modes_Of_Operation:

LC Modes of Operation
^^^^^^^^^^^^^^^^^^^^^

The `mode <FHNIntegrator.mode>` parameter of the LCControlMechanism's `FHNIntegrator` Function regulates its operation between
`"tonic" and "phasic" modes <https://www.ncbi.nlm.nih.gov/pubmed/8027789>`_:

  * in the *tonic mode* (low value of `mode <FHNIntegrator.mode>`), the output of the LCControlMechanism is moderately low
    and constant; that is, it is relatively unaffected by its `input <LCControlMechanism_Input`.  This blunts the response
    of the Mechanisms that the LCControlMechanism controls to their inputs.

  * in the *phasic mode* (high value of `mode <FHNIntegrator.mode>`), when the `input to the LC <LC_Input>` is low,
    its `output <LC_Output>` is even lower than when it is in the tonic regime, and thus the response of the
    Mechanisms it controls to their outputs is even more blunted.  However, when the LCControlMechanism's input rises above
    a certain value (determined by the `threshold <LCControlMechanism.threshold>` parameter), its output rises sharply
    generating a "phasic response", and inducing a much sharper response of the Mechanisms it controls to their inputs.

COMMENT:
XXX MENTION AGT HERE
COMMENT

COMMENT:
MOVE TO LCController
If the **mode** argument of the LCControlMechanism's constructor is specified, the following Components are also
automatically created and assigned to the LCControlMechanism when it is created:

    * an `LCController` -- takes the output of the AGTUtilityIntegratorMechanism (see below) and uses this to
      control the value of the LCControlMechanism's `mode <FHNIntegrator.mode>` attribute.  It is assigned a single
      `ControlSignal` that projects to the `ParameterState` for the LCControlMechanism's `mode <FHNIntegrator.mode>` attribute.
    ..
    * a `AGTUtilityIntegratorMechanism` -- monitors the `value <OutputState.value>` of any `OutputStates <OutputState>`
      specified in the **mode** argument of the LCControlMechanism's constructor;  these are listed in the LCControlMechanism's
      `monitored_output_states <LCControlMechanism.monitored_output_states>` attribute, as well as that attribute of the
      AGTUtilityIntegratorMechanism and LCController.  They are evaluated by the AGTUtilityIntegratorMechanism's
      `AGTUtilityIntegrator` Function, the result of whch is used by the LCControl to control the value of the
      LCControlMechanism's `mode <FHNIntegrator.mode>` attribute.
    ..
    * `MappingProjections <MappingProjection>` from Mechanisms or OutputStates specified in **monitor_for_control** to
      the AGTUtilityIntegratorMechanism's `primary InputState <InputState_Primary>`.
    ..
    * a `MappingProjection` from the AGTUtilityIntegratorMechanism's *UTILITY_SIGNAL* `OutputState
      <AGTUtilityIntegratorMechanism_Structure>` to the LCControlMechanism's *MODE* <InputState_Primary>`.
    ..
    * a `ControlProjection` from the LCController's ControlSignal to the `ParameterState` for the LCControlMechanism's
      `mode <FHNIntegrator.mode>` attribute.
COMMENT

.. _LCControlMechanism_Output:

Output
~~~~~~

COMMENT:
VERSION FOR SINGLE ControlSignal
An LCControlMechanism has a single `ControlSignal` used to modulate the function of the Mechanism(s) listed in its
`modulated_mechanisms <LCControlMechanism.modulated_mechanisms>` attribute.  The ControlSignal is assigned a
`ControlProjection` to the `ParameterState` for the `multiplicative_param <Function_Modulatory_Params>` of the
`function <Mechanism_Base.function>` for each of those Mechanisms.
COMMENT

An LCControlMechanism has a `ControlSignal` for each Mechanism listed in its `modulated_mechanisms
<LCControlMechanism.modulated_mechanisms>` attribute.  All of its ControlSignals are assigned the same value:  the result of
the LCControlMechanism's `function <LCControlMechanism.function>`.  Each ControlSignal is assigned a `ControlProjection` to the
`ParameterState` for the  `multiplicative_param <Function_Modulatory_Params>` of `function
<Mechanism_Base.function>` for the Mechanism in `modulated_mechanisms <LCControlMechanism.modulate_mechanisms>` to which it
corresponds. The Mechanisms modulated by an LCControlMechanism can be displayed using its :func:`show <LCControlMechanism.show>`
method.

.. _LCControlMechanism_Examples:

Examples
~~~~~~~~

The following example generates an LCControlMechanism that modulates the function of two TransferMechanisms, one that uses
a `Linear` function and the other a `Logistic` function::

    >>> import psyneulink as pnl
    >>> my_mech_1 = pnl.TransferMechanism(function=pnl.Linear,
    ...                                   name='my_linear_mechanism')
    >>> my_mech_2 = pnl.TransferMechanism(function=pnl.Logistic,
    ...                                   name='my_logistic_mechanism')

    >>> LC = LCControlMechanism(modulated_mechanisms=[my_mech_1, my_mech_2],
    ...                         name='my_LC')

COMMENT:
# Calling `LC.show()` generates the following report::
#
#     >>> LC.show()
#     <BLANKLINE>
#     ---------------------------------------------------------
#     <BLANKLINE>
#     my_LC
#     <BLANKLINE>
#       Monitoring the following Mechanism OutputStates:
#     <BLANKLINE>
#       Modulating the following parameters:
#         my_logistic_mechanism: gain
#         my_linear_mechanism: slope
#     <BLANKLINE>
#     ---------------------------------------------------------
COMMENT

Calling `LC.show()` generates the following report::

    my_LC

      Monitoring the following Mechanism OutputStates:

      Modulating the following parameters:
        my_logistic_mechanism: gain
        my_linear_mechanism: slope



Note that the LCControlMechanism controls the `multiplicative_param <Function_Modulatory_Params>` of the `function
<Mechanism_Base.function>` of each Mechanism:  the `gain <Logistic.gain>` parameter for ``my_mech_1``, since it uses
a `Logistic` Function; and the `slope <Linear.slope>` parameter for ``my_mech_2``, since it uses a `Linear` Function.

COMMENT:

ADDITIONAL EXAMPLES HERE OF THE DIFFERENT FORMS OF SPECIFICATION FOR
**monitor_for_control** and **modulated_mechanisms**

STRUCTURE:
MODE INPUT_STATE <- NAMED ONE, LAST?
SIGNAL INPUT_STATE(S) <- PRIMARY;  MUST BE FROM PROCESSING MECHANISMS
CONTROL SIGNALS

COMMENT

.. _LCControlMechanism_Execution:

Execution
---------

An LCControlMechanism executes within a `Composition` at a point specified in the Composition's `Scheduler` or, if it is the
`controller <System>` for a `Composition`, after all of the other Mechanisms in the Composition have `executed
<Composition_Execution>` in a `TRIAL`. It's `function <LCControlMechanism.function>` takes the `value <InputState.value>` of
the LCControlMechanism's `primary InputState <InputState_Primary>` as its input, and generates a response -- under the
influence of its `mode <FHNIntegrator.mode>` parameter -- that is assigned as the `allocation
<ControlSignal.allocation>` of its `ControlSignals <ControlSignal>`.  The latter are used by its `ControlProjections
<ControlProjection>` to modulate the response -- in the next `TRIAL` of execution --  of the Mechanisms the LCControlMechanism
controls.

.. note::
   A `ParameterState` that receives a `ControlProjection` does not update its value until its owner Mechanism
   executes (see `Lazy Evaluation <LINK>` for an explanation of "lazy" updating).  This means that even if a
   LCControlMechanism has executed, the `multiplicative_param <Function_Modulatory_Params>` parameter of the `function
   <Mechanism_Base.function>` of a Mechanism that it controls will not assume its new value until that Mechanism has
   executed.

.. _LCControlMechanism_Class_Reference:

Class Reference
---------------

"""
import typecheck as tc

from psyneulink.components.functions.function import FHNIntegrator, MULTIPLICATIVE_PARAM, ModulationParam, _is_modulation_param
from psyneulink.components.mechanisms.adaptive.control.controlmechanism import ControlMechanism
from psyneulink.components.mechanisms.processing.objectivemechanism import ObjectiveMechanism
from psyneulink.components.projections.modulatory.controlprojection import ControlProjection
from psyneulink.components.shellclasses import Mechanism, System_Base
from psyneulink.globals.context import ContextFlags
from psyneulink.globals.keywords import ALL, CONTROL_PROJECTIONS, CONTROL_SIGNALS, FUNCTION, INIT__EXECUTE__METHOD_ONLY
from psyneulink.globals.preferences.componentpreferenceset import is_pref_set
from psyneulink.globals.preferences.preferenceset import PreferenceLevel

__all__ = [
    'CONTROL_SIGNAL_NAME', 'ControlMechanismRegistry', 'LCControlMechanism', 'LCControlMechanismError',
    'MODULATED_MECHANISMS',
]

MODULATED_MECHANISMS = 'modulated_mechanisms'
CONTROL_SIGNAL_NAME = 'LCControlMechanism_ControlSignal'

ControlMechanismRegistry = {}

class LCControlMechanismError(Exception):
    def __init__(self, error_value):
        self.error_value = error_value


class LCControlMechanism(ControlMechanism):
    """
    LCControlMechanism(                     \
        system=None,                        \
        objective_mechanism=None,           \
        modulated_mechanisms=None,          \
        initial_w_FHN=0.0,                  \
        initial_v_FHN=0.0,                  \
        time_step_size_FHN=0.05,            \
        t_0_FHN=0.0,                        \
        a_v_FHN=-1/3,                       \
        b_v_FHN=0.0,                        \
        c_v_FHN=1.0,                        \
        d_v_FHN=0.0,                        \
        e_v_FHN=-1.0,                       \
        f_v_FHN=1.0,                        \
        threshold_FHN=-1.0                  \
        time_constant_v_FHN=1.0,            \
        a_w_FHN=1.0,                        \
        b_w_FHN=-0.8,                       \
        c_w_FHN=0.7,                        \
        mode_FHN=1.0,                       \
        uncorrelated_activity_FHN=0.0       \
        time_constant_w_FHN = 12.5,         \
        integration_method="RK4"        \
        base_level_gain=0.5,                \
        scaling_factor_gain=3.0,            \
        modulation=None,                    \
        params=None,                        \
        name=None,                          \
        prefs=None)

    Subclass of `ControlMechanism <AdaptiveMechanism>` that modulates the `multiplicative_param
    <Function_Modulatory_Params>` of the `function <Mechanism_Base.function>` of one or more `Mechanisms <Mechanism>`.

    Arguments
    ---------

    system : System : default None
        specifies the `System` for which the LCControlMechanism should serve as a `controller <System.controller>`;
        the LCControlMechanism will inherit any `OutputStates <OutputState>` specified in the **monitor_for_control**
        argument of the `system <EVCControlMechanism.system>`'s constructor, and any `ControlSignals <ControlSignal>`
        specified in its **control_signals** argument.

    objective_mechanism : ObjectiveMechanism, List[OutputState or Tuple[OutputState, list or 1d np.array, list or 1d
    np.array]] : default ObjectiveMechanism(function=CombineMeans)
        specifies either an `ObjectiveMechanism` to use for the LCControlMechanism or a list of the OutputStates it should
        monitor; if a list of `OutputState specifications <ObjectiveMechanism_Monitored_Output_States>` is used,
        a default ObjectiveMechanism is created and the list is passed to its **monitored_output_states** argument.

    modulated_mechanisms : List[`Mechanism`] or *ALL*
        specifies the Mechanisms to be modulated by the LCControlMechanism. If it is a list, every item must be a Mechanism
        with a `function <Mechanism_Base.function>` that implements a `multiplicative_param
        <Function_Modulatory_Params>`;  alternatively the keyword *ALL* can be used to specify all of the
        `ProcessingMechanisms <ProcessingMechanism>` in the Composition(s) to which the LCControlMechanism
        belongs.

    initial_w_FHN : float : default 0.0
        sets `initial_w <initial_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    initial_v_FHN : float : default 0.0
        sets `initial_v <initial_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    time_step_size_FHN : float : default 0.0
        sets `time_step_size <time_step_size.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    t_0_FHN : float : default 0.0
        sets `t_0 <t_0.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    a_v_FHN : float : default -1/3
        sets `a_v <a_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    b_v_FHN : float : default 0.0
        sets `b_v <b_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    c_v_FHN : float : default 1.0
        sets `c_v <c_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    d_v_FHN : float : default 0.0
        sets `d_v <d_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    e_v_FHN : float : default -1.0
        sets `e_v <e_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    f_v_FHN : float : default 1.0
        sets `f_v <f_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    threshold_FHN : float : default -1.0
        sets `threshold <threshold.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    time_constant_v_FHN : float : default 1.0
        sets `time_constant_w <time_constant_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    a_w_FHN : float : default 1.0
        sets `a_w <a_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    b_w_FHN : float : default -0.8,
        sets `b_w <b_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    c_w_FHN : float : default 0.7
        sets `c_w <c_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    mode_FHN : float : default 1.0
        sets `mode <mode.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    uncorrelated_activity_FHN : float : default 0.0
        sets `uncorrelated_activity <uncorrelated_activity.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    time_constant_w_FHN  : float : default  12.5
        sets `time_constant_w <time_constant_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    integration_method : float : default "RK4"
        sets `integration_method <integration_method.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    base_level_gain : float : default 0.5
        sets the base value in the equation used to compute the time-dependent gain value that the LCControl applies
        to each of the mechanisms it modulates

        .. math::

            g(t) = G + k w(t)

        base_level_gain = G

    scaling_factor_gain : float : default 3.0
        sets the scaling factor in the equation used to compute the time-dependent gain value that the LCControl
        applies to each of the mechanisms it modulates

        .. math::

            g(t) = G + k w(t)

        scaling_factor_gain = k

    params : Dict[param keyword: param value] : default None
        a `parameter dictionary <ParameterState_Specification>` that can be used to specify the parameters
        for the Mechanism, parameters for its function, and/or a custom function and its parameters. Values
        specified for parameters in the dictionary override any assigned to those parameters in arguments of the
        constructor.

    name : str : default see `name <LCControlMechanism.name>`
        specifies the name of the LCControlMechanism.

    prefs : PreferenceSet or specification dict : default Mechanism.classPreferences
        specifies the `PreferenceSet` for the LCControlMechanism; see `prefs <LCControlMechanism.prefs>` for details.


    Attributes
    ----------

    system : System_Base
        the `System` for which LCControlMechanism is the `controller <System.controller>`;
        the LCControlMechanism inherits any `OutputStates <OutputState>` specified in the **monitor_for_control**
        argument of the `system <EVCControlMechanism.system>`'s constructor, and any `ControlSignals <ControlSignal>`
        specified in its **control_signals** argument.

    objective_mechanism : ObjectiveMechanism : ObjectiveMechanism(function=CombinedMeans))
        the 'ObjectiveMechanism' used by the LCControlMechanism to aggregate the `value <OutputState.value>`\\s of the
        OutputStates used to drive its `phasic response <LCControlMechanism_Modes_Of_Operation>`.

    monitored_output_states : List[OutputState]
        list of the `OutputStates <OutputState>` that project to `objective_mechanism
        <EVCControlMechanism.objective_mechanism>` (and listed in its `monitored_output_states
        <ObjectiveMechanism.monitored_output_states>` attribute), and used to drive the
        LCControlMechanism's `phasic response <LCControlMechanism_Modes_Of_Operation>`.

    monitored_output_states_weights_and_exponents : List[Tuple(float, float)]
        each tuple in the list contains the weight and exponent associated with a corresponding item of
        `monitored_output_states <LCControlMechanism.monitored_output_states>`;  these are the same as those in
        the `monitored_output_states_weights_and_exponents
        <ObjectiveMechanism.monitored_output_states_weights_and_exponents>` attribute of the `objective_mechanism
        <LCControlMechanism.objective_mechanism>`, and are used by the ObjectiveMechanism's `function
        <ObjectiveMechanism.function>` to parametrize the contribution made to its output by each of the values that
        it monitors (see `ObjectiveMechanism Function <ObjectiveMechanism_Function>`).

    function : FHNIntegrator
        takes the LCControlMechanism's `input <LCControlMechanism_Input>` and generates its response <LCControlMechanism_Output>` under
        the influence of the `FHNIntegrator` Function's `mode <FHNIntegrator.mode>` attribute
        (see `LCControlMechanism_Function` for additional details).

    COMMENT:
    VERSIONS FOR SINGLE ControlSignal
        control_signals : List[ControlSignal]
            contains the LCControlMechanism's single `ControlSignal`, which sends `ControlProjections` to the
            `multiplicative_param <Function_Modulatory_Params>` of each of the Mechanisms the LCControlMechanism
            controls (listed in its `modulated_mechanisms <LCControlMechanism.modulated_mechanisms>` attribute).

        control_projections : List[ControlProjection]
            list of `ControlProjections <ControlProjection>` sent by the LCControlMechanism's `ControlSignal`, each of
            which projects to the `ParameterState` for the `multiplicative_param <Function_Modulatory_Params>` of the
            `function <Mechanism_Base.function>` of one of the Mechanisms listed in `modulated_mechanisms
            <LCControlMechanism.modulated_mechanisms>` attribute.
    COMMENT

    control_signals : List[ControlSignal]
        list of the `ControlSignals <ControlSIgnal>` for each Mechanism listed in the LCControlMechanism's
        `modulated_mechanisms <LCControlMechanism.modulated_mechanisms>` attribute  (same as the LCControlMechanism's `output_states
        <Mechanism_Base.output_states>` attribute); each sends a `ControlProjections` to the `ParameterState` for the
        `multiplicative_param <Function_Modulatory_Params>` of the `function <Mechanism_Base.function>corresponding
        Mechanism.

    control_projections : List[ControlProjection]
        list of all of the `ControlProjections <ControlProjection>` sent by the `ControlSignals <ControlSignal>` listed
        in `control_signals <LC_Mechanism.control_signals>`.

    modulated_mechanisms : List[Mechanism]
        list of `Mechanisms <Mechanism>` modulated by the LCControlMechanism.

        initial_w_FHN : float : default 0.0
        sets `initial_w <initial_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    initial_v_FHN : float : default 0.0
        sets `initial_v <initial_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    time_step_size_FHN : float : default 0.0
        sets `time_step_size <time_step_size.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    t_0_FHN : float : default 0.0
        sets `t_0 <t_0.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    a_v_FHN : float : default -1/3
        sets `a_v <a_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    b_v_FHN : float : default 0.0
        sets `b_v <b_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    c_v_FHN : float : default 1.0
        sets `c_v <c_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    d_v_FHN : float : default 0.0
        sets `d_v <d_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    e_v_FHN : float : default -1.0
        sets `e_v <e_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    f_v_FHN : float : default 1.0
        sets `f_v <f_v.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    threshold_FHN : float : default -1.0
        sets `threshold <threshold.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    time_constant_v_FHN : float : default 1.0
        sets `time_constant_w <time_constant_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    a_w_FHN : float : default 1.0
        sets `a_w <a_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    b_w_FHN : float : default -0.8,
        sets `b_w <b_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    c_w_FHN : float : default 0.7
        sets `c_w <c_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    mode_FHN : float : default 1.0
        sets `mode <mode.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    uncorrelated_activity_FHN : float : default 0.0
        sets `uncorrelated_activity <uncorrelated_activity.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    time_constant_w_FHN  : float : default  12.5
        sets `time_constant_w <time_constant_w.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    integration_method : float : default "RK4"
        sets `integration_method <integration_method.FHNIntegrator>` on the LCControlMechanism's `FHNIntegrator <FHNIntegrator>` function

    base_level_gain : float : default 0.5
        sets the base value in the equation used to compute the time-dependent gain value that the LCControl applies
        to each of the mechanisms it modulates

        .. math::

            g(t) = G + k w(t)

        base_level_gain = G

    scaling_factor_gain : float : default 3.0
        sets the scaling factor in the equation used to compute the time-dependent gain value that the LCControl
        applies to each of the mechanisms it modulates

        .. math::

            g(t) = G + k w(t)

        scaling_factor_gain = k

    modulation : ModulationParam : default ModulationParam.MULTIPLICATIVE
        the default value of `ModulationParam` that specifies the form of modulation used by the LCControlMechanism's
        `ControlProjections <ControlProjection>` unless they are `individually specified <ControlSignal_Specification>`.

    name : str
        the name of the LCControlMechanism; if it is not specified in the **name** argument of the constructor, a
        default is assigned by MechanismRegistry (see `Naming` for conventions used for default and duplicate names).

    prefs : PreferenceSet or specification dict
        the `PreferenceSet` for the LCControlMechanism; if it is not specified in the **prefs** argument of the
        constructor, a default is assigned using `classPreferences` defined in __init__.py (see :doc:`PreferenceSet
        <LINK>` for details).

    """

    componentType = "LCControlMechanism"

    initMethod = INIT__EXECUTE__METHOD_ONLY

    classPreferenceLevel = PreferenceLevel.TYPE
    # Any preferences specified below will override those specified in TypeDefaultPreferences
    # Note: only need to specify setting;  level will be assigned to TYPE automatically
    # classPreferences = {
    #     kwPreferenceSetName: 'ControlMechanismClassPreferences',
    #     kp<pref>: <setting>...}

    paramClassDefaults = ControlMechanism.paramClassDefaults.copy()
    paramClassDefaults.update({FUNCTION:FHNIntegrator,
                               CONTROL_SIGNALS: None,
                               CONTROL_PROJECTIONS: None,
                               })

    @tc.typecheck
    def __init__(self,
                 system:tc.optional(System_Base)=None,
                 objective_mechanism:tc.optional(tc.any(ObjectiveMechanism, list))=None,
                 # modulated_mechanisms:tc.optional(tc.any(list,str)) = None,
                 modulated_mechanisms=None,
                 modulation:tc.optional(_is_modulation_param)=ModulationParam.MULTIPLICATIVE,
                 integration_method="RK4",
                 initial_w_FHN=0.0,
                 initial_v_FHN=0.0,
                 time_step_size_FHN=0.05,
                 t_0_FHN=0.0,
                 a_v_FHN=-1/3,
                 b_v_FHN=0.0,
                 c_v_FHN=1.0,
                 d_v_FHN=0.0,
                 e_v_FHN=-1.0,
                 f_v_FHN=1.0,
                 time_constant_v_FHN=1.0,
                 a_w_FHN=1.0,
                 b_w_FHN=-0.8,
                 c_w_FHN=0.7,
                 threshold_FHN=-1.0,
                 time_constant_w_FHN=12.5,
                 mode_FHN=1.0,
                 uncorrelated_activity_FHN=0.0,
                 base_level_gain=0.5,
                 scaling_factor_gain=3.0,
                 params=None,
                 name=None,
                 prefs:is_pref_set=None,
                 context=None):

        # Assign args to params and functionParams dicts (kwConstants must == arg names)
        params = self._assign_args_to_param_dicts(system=system,
                                                  objective_mechanism=objective_mechanism,
                                                  modulated_mechanisms=modulated_mechanisms,
                                                  modulation=modulation,
                                                  integration_method=integration_method,
                                                  initial_v_FHN=initial_v_FHN,
                                                  initial_w_FHN=initial_w_FHN,
                                                  time_step_size_FHN=time_step_size_FHN,
                                                  t_0_FHN=t_0_FHN,
                                                  a_v_FHN=a_v_FHN,
                                                  b_v_FHN=b_v_FHN,
                                                  c_v_FHN=c_v_FHN,
                                                  d_v_FHN=d_v_FHN,
                                                  e_v_FHN=e_v_FHN,
                                                  f_v_FHN=f_v_FHN,
                                                  time_constant_v_FHN=time_constant_v_FHN,
                                                  a_w_FHN=a_w_FHN,
                                                  b_w_FHN=b_w_FHN,
                                                  c_w_FHN=c_w_FHN,
                                                  threshold_FHN=threshold_FHN,
                                                  mode_FHN=mode_FHN,
                                                  uncorrelated_activity_FHN=uncorrelated_activity_FHN,
                                                  time_constant_w_FHN=time_constant_w_FHN,
                                                  base_level_gain=base_level_gain,
                                                  scaling_factor_gain=scaling_factor_gain,
                                                  params=params)

        super().__init__(system=system,
                         objective_mechanism=objective_mechanism,
                         function=FHNIntegrator(  integration_method=integration_method,
                                                  initial_v=initial_v_FHN,
                                                  initial_w=initial_w_FHN,
                                                  time_step_size=time_step_size_FHN,
                                                  t_0=t_0_FHN,
                                                  a_v=a_v_FHN,
                                                  b_v=b_v_FHN,
                                                  c_v=c_v_FHN,
                                                  d_v=d_v_FHN,
                                                  e_v=e_v_FHN,
                                                  f_v=f_v_FHN,
                                                  time_constant_v=time_constant_v_FHN,
                                                  a_w=a_w_FHN,
                                                  b_w=b_w_FHN,
                                                  c_w=c_w_FHN,
                                                  threshold=threshold_FHN,
                                                  mode=mode_FHN,
                                                  uncorrelated_activity=uncorrelated_activity_FHN,
                                                  time_constant_w=time_constant_w_FHN,
                         ),
                         modulation=modulation,
                         params=params,
                         name=name,
                         prefs=prefs)

    def _validate_params(self, request_set, target_set=None, context=None):
        """Validate SYSTEM, MONITOR_FOR_CONTROL and CONTROL_SIGNALS

        Check that all items in MONITOR_FOR_CONTROL are Mechanisms or OutputStates for Mechanisms in self.system
        Check that every item in `modulated_mechanisms <LCControlMechanism.modulated_mechanisms>` is a Mechanism
            and that its function has a multiplicative_param
        """

        super()._validate_params(request_set=request_set,
                                 target_set=target_set,
                                 context=context)

        if MODULATED_MECHANISMS in target_set and target_set[MODULATED_MECHANISMS]:
            spec = target_set[MODULATED_MECHANISMS]

            if isinstance (spec, str):
                if not spec == ALL:
                    raise LCControlMechanismError("A string other than the keyword \'ALL\' was specified for the {} argument "
                                           "the constructor for {}".format(MODULATED_MECHANISMS, self.name))
            if not isinstance(spec, list):
                spec = [spec]

            for mech in spec:
                if not isinstance(mech, Mechanism):
                    raise LCControlMechanismError("The specification of the {} argument for {} contained an item ({})"
                                           "that is not a Mechanism.".format(MODULATED_MECHANISMS, self.name, mech))
                if not hasattr(mech.function_object, MULTIPLICATIVE_PARAM):
                    raise LCControlMechanismError("The specification of the {} argument for {} contained a Mechanism ({})"
                                           "that does not have a {}.".
                                           format(MODULATED_MECHANISMS, self.name, mech, MULTIPLICATIVE_PARAM))

    def _instantiate_output_states(self, context=None):
        """Instantiate ControlSignals and assign ControlProjections to Mechanisms in self.modulated_mechanisms

        If **modulated_mechanisms** argument of constructor was specified as *ALL*,
            assign all ProcessingMechanisms in Compositions to which LCControlMechanism belongs to self.modulated_mechanisms
        Instantiate ControlSignal with Projection to the ParameterState for the multiplicative_param of every
           Mechanism listed in self.modulated_mechanisms
        """
        from psyneulink.components.mechanisms.processing.processingmechanism import ProcessingMechanism_Base

        # *ALL* is specified for modulated_mechanisms:
        # assign all Processing Mechanisms in the LCControlMechanism's Composition(s) to its modulated_mechanisms attribute
        if isinstance(self.modulated_mechanisms, str) and self.modulated_mechanisms is ALL:
            self.modulated_mechanisms = []
            for system in self.systems:
                for mech in system.mechanisms:
                    if isinstance(mech, ProcessingMechanism_Base) and hasattr(mech.function, MULTIPLICATIVE_PARAM):
                            self.modulated_mechanisms.append(mech)
            for process in self.processes:
                for mech in process.mechanisms:
                    if isinstance(mech, ProcessingMechanism_Base) and hasattr(mech.function, MULTIPLICATIVE_PARAM):
                            self.modulated_mechanisms.append(mech)


        # # MODIFIED 9/3/17 OLD [ASSIGN ALL ControlProjections TO A SINGLE ControlSignal]
        # # Get the ParameterState for the multiplicative_param of each Mechanism in self.modulated_mechanisms
        # multiplicative_params = []
        # for mech in self.modulated_mechanisms:
        #     multiplicative_params.append(mech._parameter_states[mech.function_object.multiplicative_param])
        #
        # # Create specification for **control_signals** argument of ControlSignal constructor
        # self.control_signals = [{CONTROL_SIGNAL_NAME:multiplicative_params}]
        # MODIFIED 9/3/17 NEW [ASSIGN EACH ControlProjection TO A DIFFERENT ControlSignal]
        # Get the name of the multiplicative_param of each Mechanism in self.modulated_mechanisms
        self._control_signals = []
        if self.modulated_mechanisms:
            # Create (param_name, Mechanism) specification for **control_signals** argument of ControlSignal constructor
            if not isinstance(self.modulated_mechanisms, list):
                self._modulated_mechanisms = [self.modulated_mechanisms]
            multiplicative_param_names = []
            for mech in self.modulated_mechanisms:
                multiplicative_param_names.append(mech.function_object.multiplicative_param)
            for mech, mult_param_name in zip(self.modulated_mechanisms, multiplicative_param_names):
                self._control_signals.append((mult_param_name, mech))
        # MODIFIED 9/3/17 END
        super()._instantiate_output_states(context=context)

    def _execute(
        self,
        variable=None,
        function_variable=None,
        runtime_params=None,
        context=None
    ):
        """Updates LCControlMechanism's ControlSignal based on input and mode parameter value
        """
        # IMPLEMENTATION NOTE:  skip ControlMechanism._execute since it is a stub method that returns input_values
        output_values = super(ControlMechanism, self)._execute(
            variable=variable,
            function_variable=function_variable,
            runtime_params=runtime_params,
            context=context
        )

        gain_t = self.scaling_factor_gain*output_values[1] + self.base_level_gain

        # # MODIFIED 1/17/18 OLD:
        return gain_t, gain_t, output_values[0], output_values[1], output_values[2]
        # # MODIFIED 1/17/18 NEW:
        # output_values = np.array(output_values).reshape(3,1)
        # return np.vstack((gain_t, gain_t, output_values))
        # # MODIFIED 1/17/18 END



    @tc.typecheck
    def add_modulated_mechanisms(self, mechanisms:list):
        """Add ControlProjections to the specified Mechanisms.
        """

        request_set = {MODULATED_MECHANISMS:mechanisms}
        target_set = {}
        self._validate_params(request_set=request_set, target_set=target_set)

        # Assign ControlProjection from the LCControlMechanism's ControlSignal
        #    to the ParameterState for the multiplicative_param of each Mechanism in mechanisms
        multiplicative_params = []
        for mech in mechanisms:
            self.modulated_mechanisms.append(mech)
            parameter_state = mech._parameter_states[mech.multiplicative_param]
            ControlProjection(sender=self.control_signals[0],
                              receiver=parameter_state)

    @tc.typecheck
    def remove_modulated_mechanisms(self, mechanisms:list):
        """Remove the ControlProjections to the specified Mechanisms.
        """

        for mech in mechanisms:
            if not mech in self.modulated_mechanisms:
                continue

            parameter_state = mech._parameter_states[mech.multiplicative_param]

            # Get ControlProjection
            for projection in parameter_state.mod_afferents:
                if projection.sender.owner is self:
                    control_projection = projection
                    break

            # Delete ControlProjection ControlSignal's list of efferents
            index = self.control_signals[0].efferents[control_projection]
            del(self.control_signals[0].efferents[index])

            # Delete ControlProjection from recipient ParameterState
            index = parameter_state.mod_afferents[control_projection]
            del(parameter_state.mod_afferents[index])

            # Delete Mechanism from self.modulated_mechanisms
            index = self.modulated_mechanisms.index(mech)
            del(self.modulated_mechanisms[index])

    def show(self):
        """Display the `OutputStates <OutputState>` monitored by the LCControlMechanism's `objective_mechanism`
        and the `multiplicative_params <Function_Modulatory_Params>` modulated by the LCControlMechanism.
        """

        print("\n---------------------------------------------------------")

        print("\n{0}".format(self.name))
        print("\n\tMonitoring the following Mechanism OutputStates:")
        if self.objective_mechanism is None:
            print("\t\tNone")
        else:
            for state in self.objective_mechanism.input_states:
                for projection in state.path_afferents:
                    monitored_state = projection.sender
                    monitored_state_mech = projection.sender.owner
                    monitored_state_index = self.monitored_output_states.index(monitored_state)

                    weight = self.monitored_output_states_weights_and_exponents[monitored_state_index][0]
                    exponent = self.monitored_output_states_weights_and_exponents[monitored_state_index][1]

                    print ("\t\t{0}: {1} (exp: {2}; wt: {3})".
                           format(monitored_state_mech.name, monitored_state.name, weight, exponent))

        print ("\n\tModulating the following parameters:".format(self.name))
        # Sort for consistency of output:
        state_names_sorted = sorted(self.output_states.names)
        for state_name in state_names_sorted:
            for projection in self.output_states[state_name].efferents:
                print ("\t\t{0}: {1}".format(projection.receiver.owner.name, projection.receiver.name))

        print ("\n---------------------------------------------------------")
