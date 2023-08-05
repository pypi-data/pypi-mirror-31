# -*- coding: utf-8 -*-

"""
This module defines :class:`AbstractJob`, that is the base class
for all the jobs in a Scheduler, as well as a basic concrete subclass
:class:`Job` for creating a job from a coroutine.

It also defines a couple of simple job classes.
"""

import sys
import asyncio

debug = False                               # pylint: disable=C0103
debug = True                                # pylint: disable=C0103

# pylint settings
# W0212: we have a lot of accesses to protected members of other classes
# R0914 Too many local variables
# pylint: disable=W0212


# my first inclination had been to specialize asyncio.Task
# it does not work well though, because you want to model
# dependencies **before** anything starts, of course
# but in asyncio, creating a Task object implies scheduling that for execution

# so, let's have it the other way around
# what we need is a way to attach our own Job instance to the corresp.
# Task instance (and back) right after Task creation, so that
# (*) once asyncio.wait is done, we can easily find out
#     wich Jobs are done or pending
# (*) from one Job, easily know what its status is by
#     looking into its Task obj - if already scheduled

# Scheduler == graph
# Job == node


class AbstractJob:                                      # pylint: disable=R0902
    """
    AbstractJob is a virtual class:

    * it offers some very basic graph-related features
      to model requirements *a la* Makefile;
    * its subclasses are expected to implement a `co_run()`
      and a `co_shutdown()` methods that specify
      the actual behaviour of the job, as coroutines.
    * AbstractJob is mostly a companion class to the
      :class:`~asynciojobs.scheduler.Scheduler` class,
      that triggers these co_* methods.

    **Life Cycle**: AbstractJob is also aware of a common life cycle
    for all jobs, which can be summarized as follows:

      **idle** → **scheduled** → **running** → **done**

    In un-windowed schedulers, there is no distinction between
    scheduled and running. In other words, in this case a job goes directly
    from **idle** to **running**.a

    On the other hand, in windowed orchestrations - see the ``jobs_window``
    parameter to :meth:`~asynciojobs.scheduler.Scheduler.co_orchestrate` -
    a job can be scheduled but not yet running, because it is waiting
    for a slot in the global window.

    Args:

        forever (bool): if set, means the job
          is not returning at all and runs forever;
          in this case ``Scheduler.orchestrate()``
          will not wait for that job, and will terminate it
          once all the regular - i.e. not-forever - jobs are done.

        critical (bool): if set,
          this flag indicates that any exception raised during the
          execution of that job should result in the scheduler
          aborting its run immediately. The default behaviour
          is to let the scheduler finish its jobs, at which point
          the jobs can be inspected for exceptions or results.

        required: this can be one, or a collection of, jobs that will
          make the job's requirements;
          requirements can be added later on as well.

        label (str): for convenience mostly, allows to specify
          the way that particular job should be displayed by the scheduler,
          either in textual form by ``Scheduler.list()``, or in graphical form
          by ``Scheduler.graph()``. See also :meth:`text_label()`
          and :meth:`graph_label()` for how this is used.

          As far as labelling, each subclass of :class:`AbstractJob`
          implements a default labelling scheme, so it is not mandatory
          to set a specific label on each job instance, however it is
          sometimes useful.

          Labels must not be confused with details, see :meth:`details()`

        scheduler: this can be an instance of a
          :class:`~asynciojobs.scheduler.Scheduler` object, in which
          the newly created job instance is immediately added.
          A job instance can also be inserted in a scheduler instance later on.

    **Note**: a Job instance must only be added in **one Scheduler instance**
    at most - be aware that the code makes no control on this property,
    but be aware that odd behaviours can be observed if it is not fulfilled.
    """

    def __init__(self, *,                               # pylint: disable=R0913
                 forever=False, critical=False, label=None,
                 required=None, scheduler=None):
        self.forever = forever
        self.critical = critical
        # access to labelling is done through methods
        self.label = label
        # for convenience, one can mention
        # only one, or a collection of, AbstractJobs
        self.required = set()
        self.requires(required)
        # convenience again
        if scheduler is not None:
            scheduler.add(self)
        # once submitted in the asyncio loop/scheduler,
        # `co_run()` gets embedded in a Task object,
        # that is our handle when talking to asyncio.wait
        self._task = None
        # this is updated by the Window class when the job makes it through
        self._running = False
        # ==== fields for our friend Scheduler all start with _s_
        # this is for graph browsing algos
        self._s_mark = None
        # the reverse of required
        self._s_successors = set()
        # this attribute is reserved for use by the scheduler
        # that will for example store there an ordering information,
        # which in turn can be used for printing relationships
        # by Scheduler.list() and similar
        self._sched_id = None

    def _get_sched_id(self):
        return self._sched_id or '??'

    def _get_text_label(self):
        # In terms of labelling, things have become a little tricky over
        # time. When listing an instance of Scheduler, there are 2 ways
        # we need to show a job
        #
        # * first there is a plain label, that may be set at creation time
        #
        # * second, when showing references (like the jobs that a given job
        #  requires), we show ids like '01' and similar.
        # Except that, the job itself has no idea about that at first,
        # it's the Scheduler instance that decides on that.
        #
        # so:
        # * if use_sched_id is True, looks in self._sched_id that is expected
        # to have been set by companion class Scheduler;
        # if not set returns a warning msg '??'
        #
        # * otherwise, i.e. if use_sched_id is False, looks for the label
        #  used at creation-time, and otherwise runs its class's
        #  `text_label()` method

        # use instance-specific label if set
        attempt = self.label
        if attempt is not None:
            return attempt
        # otherwise, try self.text_label() and use that
        attempt = self.text_label()
        if attempt is not None:
            return attempt
        # otherwise
        return "NOLABEL"

    def _get_graph_label(self):
        # a similar logic for a graphical label
        # we don't need to bother about _sched_id here though
        # also we try graph_label() first, and resort to text_label()
        # if it's not redefined on the object
        attempt = self.graph_label()
        if attempt is not None:
            return attempt
        return self._get_text_label()

    def text_label(self):
        """
        This method is intended to be redefined by daughter classes.

        Returns:
          a one-line string that describes this job.

        This representation for the job is used by the Scheduler object
        through its :meth:`~asynciojobs.scheduler.Scheduler.list()` and
        :meth:`~asynciojobs.scheduler.Scheduler.debrief()` methods, i.e.
        when a scheduler is printed out in textual format.

        The overall logic is to always use the instance's ``label`` attribute
        if set, or to use this method otherwise. If none of this returns
        anything useful, the textual label used is ``NOLABEL``.
        """
        pass

    def graph_label(self):
        """
        This method is intended to be redefined by daughter classes.

        Returns:
          a string used by the Scheduler methods
          that produce a graph, such as
          :meth:`~asynciojobs.scheduler.Scheduler.graph` and
          :meth:`~asynciojobs.scheduler.Scheduler.export_as_dotfile`.

        Because of the way graphs are presented, it can have contain "newline"
        characters, that will render as line breaks in the output graph.

        If this method is not defined on a concrete class,
        then the :meth:`text_label()` method is used instead.
        """
        pass

    ##########
    _has_support_for_unicode = None  # type: bool

    @classmethod
    def _detect_support_for_unicode(cls):
        if cls._has_support_for_unicode is None:
            try:
                cls._c_saltire.encode(sys.stdout.encoding)
                cls._has_support_for_unicode = True
            except UnicodeEncodeError:
                cls._has_support_for_unicode = False
        return cls._has_support_for_unicode

    # unicode version
    # _c_frowning_face = "\u2639" # ☹
    # _c_smiling_face  = "\u263b" # ☻
    _c_saltire = "\u2613"       # ☓
    _c_circle_arrow = "\u21ba"  # ↺
    _c_black_flag = "\u2691"    # ⚑
    _c_white_flag = "\u2690"    # ⚐
    _c_warning = "\u26a0"       # ⚠
    _c_black_star = "\u2605"    # ★
    _c_sun = "\u2609"           # ☉
    _c_infinity = "\u221e"      # ∞

    def _short_unicode(self):
        """
        A small (7 chars) badge that summarizes the job's internal attributes
        uses non-ASCII characters
        """
        # where is it in the lifecycle
        c_running = self._c_saltire if self.is_done() else \
            self._c_circle_arrow if self.is_running() else \
            self._c_black_flag if self.is_scheduled() else \
            self._c_white_flag
        # is it critical or not ?
        c_crit = self._c_warning if self.is_critical() else " "
        # has it raised an exception or not ?
        c_boom = self._c_black_star if self.raised_exception() \
            else self._c_sun if self.is_running() \
            else " "
        # is it going forever or not
        c_forever = self._c_infinity if self.forever else " "

        # add extra white space as unicode chars in terminal tend to be wider
        # than others
        return "{} {} {} {}".format(c_crit, c_boom, c_running, c_forever)

    def _short_ascii(self):
        """
        A small (7 chars) badge that summarizes the job's internal attributes
        uses ASCII-only characters
        """
        # where is it in the lifecycle
        c_running = "x" if self.is_done() else \
            "o" if self.is_running() else \
            "." if self.is_scheduled() else \
            ">"
        # is it critical or not ?
        c_crit = "!" if self.is_critical() else " "
        # has it raised an exception or not ?
        c_boom = ":(" if self.raised_exception() \
                 else ":)" if self.is_running() \
                 else "  "
        # is it going forever or not
        c_forever = "8" if self.forever else " "

        # add extra white space as unicode chars in terminal tend to be wider
        # than others
        return "{} {} {} {}".format(c_crit, c_boom, c_running, c_forever)

    def short(self):
        """
        Returns:
          a 4 characters string (in fact 7 with interspaces)
          that summarizes the 4 dimensions of the job, that is to say

        * its point in the lifecycle (idle → scheduled → running → done)

        * is it declared as forever

        * is it declared as critical

        * did it trigger an exception

        """
        if self._detect_support_for_unicode():
            return self._short_unicode()
        return self._short_ascii()

    def _repr(self, show_requires=True, show_result_or_exception=True):
        """
        returns a string that describes this job instance,
        with contents as specified
        """
        info = self.short()
        info += " <{} `{}`>".format(type(self).__name__,
                                    self._get_text_label())

        if show_result_or_exception:
            exception = self.raised_exception()
            if exception:
                critical_msg = "CRIT. EXC." if self.is_critical() \
                               else "exception"
                info += "!! {} => {}:{}!!"\
                        .format(critical_msg,
                                type(exception).__name__, exception)
            elif self.is_done():
                info += "[[ -> {}]]".format(self.result())

        # show dependencies in both directions
        if show_requires and self.required:
            info += " - requires {"
            info += ", ".join(req._get_sched_id()       # pylint: disable=e1101
                              for req in self.required)
            info += "}"
        return info

    def __repr__(self):
        return self._repr(show_requires=False)

    def requires(self, *requirements):
        """
        Arguments:
          requirements: an iterable of `AbstractJob`
            instances that are added to the requirements.

        For convenience, any nested structure made of job instances
        can be provided, and if None objects are found, they are silently
        ignored. For example, with `j{1,2,3,4}` being jobs or sequences,
        all the following calls are legitimate:

        * ``j1.requires(None)``
        * ``j1.requires([None])``
        * ``j1.requires((None,))``
        * ``j1.requires(j2)``
        * ``j1.requires(j2, j3)``
        * ``j1.requires([j2, j3])``
        * ``j1.requires(j2, [j3, j4])``
        * ``j1.requires((j2, j3))``
        * ``j1.requires(([j2], [[[j3]]]))``
        """
        from .sequence import Sequence
        for requirement in requirements:
            if requirement is None:
                continue
            if isinstance(requirement, AbstractJob):
                self.required.add(requirement)
            elif isinstance(requirement, Sequence):
                if requirement.jobs:
                    self.required.add(requirement.jobs[-1])
            elif isinstance(requirement, (tuple, list)):
                for req in requirement:
                    self.requires(req)
            # not quite sure about what do to here in fact
            else:
                print("WARNING: fishy requirement in AbstractJob.requires")
                self.requires(list(requirement))

    def is_idle(self):
        """
        Returns:
          bool: ``True`` if the job has not been scheduled already, which
          in other words means that at least one of its requirements
          is not fulfilled.

        Implies `not is_scheduled()`, and so *a fortiori*
        `not is_running` and `not is_done()`.

        """
        return self._task is None

    def is_scheduled(self):
        """
        Returns:
          bool: ``True`` if the job has been scheduled.

        If True, it means that the job's requirements are met, and it has
        proceeded to the windowing system; equivalent to `not is_idle()`.
        """
        return self._task is not None

    def is_running(self):
        """
        Returns:
          bool: once a job starts, it tries to get a slot
          in the windowing sytem. This method returns ``True`` if the job
          has received the green light from the windowing system.
          Implies `is_scheduled()`.
        """
        return self._running

    def is_done(self):
        """
        Returns:
          bool: ``True`` if the job has completed.

        If this method returns ``True``, it implies that
        `is_scheduled()` and `is_running()`
        would also return ``True`` at that time.
        """
        return self._task is not None \
            and self._task._state == asyncio.futures._FINISHED

    def raised_exception(self):
        """
        Returns:
          an exception if the job has completed by raising an exception,
          and None otherwise.
        """
        return self._task is not None and self._task._exception

    def is_critical(self):
        """
        Returns:
          bool: whether this job is a critical job or not.
        """
        return self.critical

    def result(self):
        """
        Returns:
          When this job is completed and has not raised an exception, this
          method lets you retrieve the job's result. i.e. the value returned
          by its `co_run()` method.
        """
        if not self.is_done():
            raise ValueError("job not finished")
        return self._task._result

    async def co_run(self):
        """
        Abstract virtual - needs to be implemented
        """
        print("AbstractJob.co_run() needs to be implemented on class {}"
              .format(self.__class__.__name__))

    async def co_shutdown(self):
        """
        Abstract virtual - needs to be implemented
        """
        print("AbstractJob.co_shutdown() needs to be implemented on class {}"
              .format(self.__class__.__name__))

    def standalone_run(self):
        """
        A convenience helper that just runs this one job on its own.

        Mostly useful for debugging the internals of that job,
        e.g. for checking for gross mistakes and other exceptions.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.co_run())

    def details(self):
        """
        An optional method to implement on concrete job classes; if it
        returns a non None value, these additional details about that job
        will get printed by
        :meth:`asynciojobs.scheduler.Scheduler.list()` and
        :meth:`asynciojobs.scheduler.Scheduler.debrief()`
        when called with `details=True`.
        """
        pass


class Job(AbstractJob):

    """
    The simplest concrete job class, for building an instance of AbstractJob
    from of a python coroutine.

    Parameters:

      corun: a coroutine to be evaluated when the job runs
      coshutdown: an optional coroutine to be evaluated when the scheduler
        is done running
      scheduler: passed to :class:`AbstractJob`
      required: passed to :class:`AbstractJob`
      label: passed to :class:`AbstractJob`

    Example:
      To create a job that prints a message and waits for a fixed delay::

        async def aprint(message, delay):
            print(message)
            await asyncio.sleep(delay)

        j = Job(aprint("Welcome - idling for 3 seconds", 3))
    """

    def __init__(self, corun, *args, coshutdown=None, **kwds):
        self.corun = corun
        self.coshutdown = coshutdown
        super().__init__(*args, **kwds)

    def text_label(self):
        """
        Implementation of the method expected by :class:`AbstractJob`
        """
        try:
            return "Job[{name} (...)]".format(name=self.corun.__name__)
        except Exception:                                # pylint:disable=w0703
            return "Job instance"

    async def co_run(self):
        """
        Implementation of the method expected by :class:`AbstractJob`
        """
        result = await self.corun
        return result

    async def co_shutdown(self):
        """
        Implementation of the method expected by :class:`AbstractJob`,
        or more exactly by :meth:`asynciojobs.scheduler.Scheduler.list`
        """
        if self.coshutdown:
            result = await self.coshutdown
            return result

####################


class _PrintJob(AbstractJob):
    """
    A job that just prints messages, and optionnally sleeps for some time.

    Parameters:

      messages: passed to ``print`` as-is
      sleep: optional, an int or float describing in seconds
        how long to sleep after the messages get printed
      banner: optional, a fixed text printed out before the messages
       like e.g. ``40*'='``; it won't make it into ``details()``
      scheduler: passed to :class:``AbstractJob``
      required: passed to :class:``AbstractJob``
      label: passed to :class:``AbstractJob``
    """

    def __init__(self, *messages, sleep=None, banner=None,
                 # these are for AbstractJob
                 scheduler=None,
                 label=None, required=None):
        self.messages = messages
        self.sleep = sleep
        self.banner = banner
        super().__init__(label=label, required=required, scheduler=scheduler)

    async def co_run(self):
        """
        Implementation of the method expected by :class:`AbstractJob`
        """
        try:
            if self.banner:
                print(self.banner + " ", end="")
            print(*self.messages)
            if self.sleep:
                print("Sleeping for {}s".format(self.sleep))
                await asyncio.sleep(self.sleep)
        except Exception:                               # pylint: disable=W0703
            # should not happen, but if it does we need to know why
            import traceback
            traceback.print_exc()

    async def co_shutdown(self):
        """
        Implementation of the method expected by :class:`AbstractJob`;
        does nothing.
        """
        pass

    def details(self):                                  # pylint: disable=C0111
        """
        Implementation of the method expected by :class:`AbstractJob`
        """
        result = ""
        if self.sleep:
            result += "[+ sleep {}s] ".format(self.sleep)
        result += "msg= "
        result += self.messages[0]
        result += "..." if len(self.messages) > 1 else ""
        return result
