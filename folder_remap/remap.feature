Feature: Automatic remapping of samples to the needed Refgenome versions

	Given there are multiple Refgenome versions and dependent Workflows
	When a new sample is created
	Then a remapped Sample should have been calculated or an Error message shown and reported to the maintainer
