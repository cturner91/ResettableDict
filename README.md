# Coding Challenge - ResettableDict

This was a live coding challenge for a recent interview. The brief was to create a dict-like object with `set`, `get` and `delete` methods for attributes. It should also have a `commit` method which persists data to a local 'database', and a `reset` method which removes all uncommitted changes. At all times, we should be able to get the length of the object.

The details of specific circumstances were discussed during the interview. In a nutshell, they are:
* User should be able to `get` a value even if the key is uncommitted.
* If a key exists in both committed and uncommitted states, priorty should be given to the uncommitted state.
* If delete is called, the value in uncommitted should be deleted and the value in committed should be deleted during the next commit.
* If `reset` is called, then all uncommitted changes are dropped and the committed state is unchanged.

I may have missed some of the requirements here, hopefully they are clear from the tests.

## Did I learn anything?

Owing to time pressures, I tried to cut corners in one test and test 2-3 features in the same test. However, I forgot to wipe the local instance, leading to tests failing unexpectedly that then took even longer to debug. Lesson learned - don't cut corners, do it properly.

