.. _quickstart

Example
=======

.. code-block:: python
	def example_histogram():
	    c = 600
	    d = int(c**2)
	    a = np.zeros((1, d))
	    t = 200
	    a[0, 0] = 1
	    a[0, 1] = 2
	    a[0, 2] = 3
	    a[0, 3] = 4
	    a[0, 4] = 5
	    b = [np.roll(a, shift=i, axis=1) for i in range(t)]
	    return np.roll(np.array(b).reshape(t, c, c), shift=4, axis=0)



	def main():
	    ax = plt.axes()
	    ax.hist(np.random.rand(300, 160, 160), compact=True)
	    ax.set_xlabel("x-axis")
	    ax.set_ylabel("y-axis")
	    ax.x_axis(start=-4, end=10)
	    ax.y_axis(start=300, end=400)
	    ax.set_loop()
	    ax.cmap(
	        colors=["black", "pink", "steelblue", "green", "white"],
	        positions=[0, 0.25, 0.5, 0.75, 1],
	    )
	    ax.x_unit(unit="pc")
	    ax.y_unit(unit="pc")
	    ax.t_unit(unit="Myr")
	    ax.savefig("test.json")
